<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import type { EChartsOption } from 'echarts'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import DataPanel from '../components/DataPanel.vue'
import FinanceChart from '../components/FinanceChart.vue'
import PageHeader from '../components/PageHeader.vue'
import { useFinanceStore } from '../stores/finance'
import type { MonthlyBudget } from '../types/finance'
import { money, numberValue } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const year = ref(new Date().getFullYear())
const rows = ref<MonthlyBudget[]>([])
const loading = ref(false)

const columns: DataTableColumns<MonthlyBudget> = [
  { title: '月份', key: 'month', width: 110 },
  { title: '工资收入', key: 'salary_income', align: 'right', render: (row) => money(row.salary_income) },
  { title: '非工资收入', key: 'non_salary_income', align: 'right', render: (row) => money(row.non_salary_income) },
  { title: '额外收入', key: 'extra_income', align: 'right', render: (row) => money(row.extra_income) },
  { title: '建议储蓄/还债', key: 'recommended_saving_debt', align: 'right', render: (row) => money(row.recommended_saving_debt) },
  { title: '本月结余', key: 'monthly_surplus', align: 'right', render: (row) => money(row.monthly_surplus) },
  { title: '状态', key: 'status' }
]

const chartOption = computed<EChartsOption>(() => ({
  color: ['#cc785c', '#5db8a6', '#e8a55a'],
  tooltip: { trigger: 'axis' },
  legend: { bottom: 0 },
  grid: { left: 42, right: 20, top: 24, bottom: 56 },
  xAxis: { type: 'category', data: rows.value.map((item) => item.month.slice(5, 7)) },
  yAxis: { type: 'value' },
  series: [
    { name: '工资收入', type: 'line', smooth: true, data: rows.value.map((item) => numberValue(item.salary_income)) },
    { name: '非工资收入', type: 'bar', data: rows.value.map((item) => numberValue(item.non_salary_income)) },
    { name: '额外收入', type: 'bar', data: rows.value.map((item) => numberValue(item.extra_income)) }
  ]
}))

async function load() {
  loading.value = true
  try {
    const plan = await finance.incomePlan(year.value)
    rows.value = plan.months
  } catch (error) {
    message.error(error instanceof Error ? error.message : '收入规划加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <PageHeader
    eyebrow="Income"
    title="收入规划"
    description="跟踪工资区间、非工资收入和额外收入分配，避免日常预算被偶发收入抬高。"
  >
    <template #actions>
      <n-space>
        <n-input-number v-model:value="year" class="year-control" :show-button="false" />
        <n-button type="primary" :loading="loading" @click="load">刷新</n-button>
      </n-space>
    </template>
  </PageHeader>
  <DataPanel title="年度收入趋势">
    <FinanceChart :option="chartOption" :height="340" />
  </DataPanel>
  <DataPanel title="月份明细">
    <n-data-table :columns="columns" :data="rows" :loading="loading" :bordered="false" size="small" />
  </DataPanel>
</template>
