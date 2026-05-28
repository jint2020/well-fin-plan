<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import DataPanel from '../components/DataPanel.vue'
import FinanceChart from '../components/FinanceChart.vue'
import MetricCard from '../components/MetricCard.vue'
import PageHeader from '../components/PageHeader.vue'
import { useFinanceStore } from '../stores/finance'
import type { MonthlyBudget } from '../types/finance'
import { currentMonth, money, numberValue, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const month = ref(currentMonth())
const budget = ref<MonthlyBudget | null>(null)
const loading = ref(false)

const cards = computed(() => {
  if (!budget.value) return []
  return [
    { title: '预算采用收入', value: money(budget.value.budget_income) },
    { title: '实际总收入', value: money(budget.value.actual_total_income), tone: 'good' as const },
    { title: '额外收入', value: money(budget.value.extra_income) },
    { title: '本月结余', value: money(budget.value.monthly_surplus), tone: 'good' as const },
    { title: '储蓄/偿债率', value: percent(budget.value.saving_debt_rate), tone: 'warn' as const },
    { title: '状态', value: budget.value.status }
  ]
})

const chartOption = computed<EChartsOption>(() => {
  const item = budget.value
  if (!item) return {}
  return {
    color: ['#cc785c', '#5db8a6'],
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 42, right: 20, top: 24, bottom: 56 },
    xAxis: { type: 'category', data: ['必要', '储蓄/还债', '准备金', '弹性'] },
    yAxis: { type: 'value' },
    series: [
      {
        name: '建议',
        type: 'bar',
        data: [
          numberValue(item.necessary_budget),
          numberValue(item.recommended_saving_debt),
          numberValue(item.recommended_reserve),
          numberValue(item.recommended_flex)
        ]
      },
      {
        name: '实际',
        type: 'bar',
        data: [
          numberValue(item.actual_necessary),
          numberValue(item.actual_saving_investment) + numberValue(item.actual_debt_payment),
          numberValue(item.actual_reserve),
          numberValue(item.actual_flex)
        ]
      }
    ]
  }
})

async function load() {
  loading.value = true
  try {
    budget.value = await finance.monthlyBudget(month.value)
  } catch (error) {
    message.error(error instanceof Error ? error.message : '月度预算加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <PageHeader
    eyebrow="Budget"
    title="月度预算"
    description="基础预算只按保守预算基准计算，额外收入按 70/20/10 单独分配。"
  >
    <template #actions>
      <n-space>
        <n-input v-model:value="month" class="month-control" placeholder="YYYY-MM" @keyup.enter="load" />
        <n-button type="primary" :loading="loading" @click="load">计算</n-button>
      </n-space>
    </template>
  </PageHeader>
  <div class="metric-grid metric-grid--compact">
    <MetricCard v-for="item in cards" :key="item.title" v-bind="item" />
  </div>
  <DataPanel title="建议预算 vs 实际执行">
    <FinanceChart :option="chartOption" :height="360" />
  </DataPanel>
</template>
