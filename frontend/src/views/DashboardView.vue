<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { Banknote, CircleDollarSign, PiggyBank, TrendingUp, WalletCards } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import DataPanel from '../components/DataPanel.vue'
import FinanceChart from '../components/FinanceChart.vue'
import MetricCard from '../components/MetricCard.vue'
import PageHeader from '../components/PageHeader.vue'
import { useFinanceStore } from '../stores/finance'
import { money, numberValue, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const month = ref(finance.activeMonth)

const dashboard = computed(() => finance.dashboard)
const budget = computed(() => dashboard.value?.monthly_budget)
const expense = computed(() => dashboard.value?.expense_summary)

const requiredMetrics = computed(() => {
  if (!budget.value || !expense.value || !dashboard.value) return []
  return [
    { title: '本月总收入', value: money(budget.value.actual_total_income), icon: CircleDollarSign },
    { title: '工资收入', value: money(budget.value.salary_income), icon: Banknote },
    { title: '非工资收入', value: money(budget.value.non_salary_income), icon: WalletCards },
    { title: '额外收入', value: money(budget.value.extra_income), icon: TrendingUp, tone: 'good' as const },
    { title: '本月总支出', value: money(expense.value.total_expense), icon: PiggyBank },
    { title: '本月结余', value: money(budget.value.monthly_surplus), icon: WalletCards, tone: 'good' as const },
    { title: '储蓄/偿债率', value: percent(budget.value.saving_debt_rate), icon: TrendingUp },
    {
      title: '应急金达成率',
      value: percent(dashboard.value.emergency_fund_progress.progress_rate),
      caption: `${money(dashboard.value.emergency_fund_balance)} / ${money(dashboard.value.emergency_fund_progress.target_amount)}`,
      icon: PiggyBank,
      tone: 'warn' as const
    }
  ]
})

const budgetChart = computed<EChartsOption>(() => {
  const item = budget.value
  if (!item) return {}
  return {
    color: ['#cc785c', '#5db8a6'],
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 36, right: 20, top: 24, bottom: 56 },
    xAxis: { type: 'category', data: ['必要', '储蓄投资', '还债', '准备金', '弹性'] },
    yAxis: { type: 'value' },
    series: [
      {
        name: '建议',
        type: 'bar',
        data: [
          numberValue(item.necessary_budget),
          numberValue(item.recommended_saving_debt),
          0,
          numberValue(item.recommended_reserve),
          numberValue(item.recommended_flex)
        ]
      },
      {
        name: '实际',
        type: 'bar',
        data: [
          numberValue(item.actual_necessary),
          numberValue(item.actual_saving_investment),
          numberValue(item.actual_debt_payment),
          numberValue(item.actual_reserve),
          numberValue(item.actual_flex)
        ]
      }
    ]
  }
})

const assetChart = computed<EChartsOption>(() => ({
  color: ['#cc785c', '#5db8a6', '#e8a55a', '#5db872', '#8e8b82'],
  tooltip: { trigger: 'item' },
  series: [
    {
      name: '资产配置',
      type: 'pie',
      radius: ['48%', '72%'],
      data:
        dashboard.value?.asset_allocation_summary.items.map((item) => ({
          name: item.asset_class,
          value: numberValue(item.current_amount)
        })) ?? []
    }
  ]
}))

async function load() {
  try {
    await finance.loadDashboard(month.value)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '仪表盘加载失败')
  }
}

onMounted(load)
</script>

<template>
  <PageHeader
    eyebrow="Dashboard"
    title="月度仪表盘"
    description="用一个月视角跟踪收入、支出、结余、储蓄偿债和应急金进度。"
  >
    <template #actions>
      <n-space align="center">
        <n-input v-model:value="month" class="month-control" placeholder="YYYY-MM" @keyup.enter="load" />
        <n-button type="primary" :loading="finance.loading" @click="load">刷新</n-button>
      </n-space>
    </template>
  </PageHeader>

  <div v-if="dashboard" class="metric-grid">
    <MetricCard
      v-for="item in requiredMetrics"
      :key="item.title"
      :title="item.title"
      :value="item.value"
      :caption="item.caption"
      :icon="item.icon"
      :tone="item.tone"
    />
  </div>

  <div v-if="dashboard" class="dashboard-grid">
    <DataPanel title="预算 vs 实际" description="必要支出、储蓄投资、还债、准备金和弹性消费的月度对比。">
      <FinanceChart :option="budgetChart" :height="340" />
    </DataPanel>
    <DataPanel title="资产配置" description="按当前金额计算的资产分布。">
      <FinanceChart :option="assetChart" :height="340" />
    </DataPanel>
  </div>

  <div v-if="dashboard" class="summary-strip">
    <DataPanel title="风险与目标概览">
      <div class="progress-row">
        <span>应急金</span>
        <n-progress type="line" :percentage="numberValue(dashboard.emergency_fund_progress.progress_rate) * 100" />
      </div>
      <div class="progress-row">
        <span>债务还款</span>
        <n-progress type="line" :percentage="numberValue(dashboard.debt_progress.repayment_completion_rate) * 100" />
      </div>
      <div class="progress-row">
        <span>目标计划</span>
        <n-progress type="line" :percentage="numberValue(dashboard.goal_progress.overall_progress_rate) * 100" />
      </div>
    </DataPanel>
  </div>

  <n-empty v-else description="暂无仪表盘数据，请登录并录入流水。" />
</template>
