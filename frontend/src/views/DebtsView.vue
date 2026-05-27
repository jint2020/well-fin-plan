<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import CrudTablePage from '../components/CrudTablePage.vue'
import DataPanel from '../components/DataPanel.vue'
import MetricCard from '../components/MetricCard.vue'
import { useFinanceStore } from '../stores/finance'
import type { Debt, DebtProgress } from '../types/finance'
import { currentMonth, money, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const rows = ref<Debt[]>([])
const progress = ref<DebtProgress | null>(null)
const month = ref(currentMonth())
const loading = ref(false)

const fields = [
  { key: 'name', label: '债务名称' },
  { key: 'current_balance', label: '当前余额' },
  { key: 'annual_rate', label: '年利率' },
  { key: 'minimum_monthly_payment', label: '最低月还款' },
  { key: 'extra_monthly_payment', label: '额外还款' },
  {
    key: 'status',
    label: '状态',
    type: 'select' as const,
    options: [
      { label: '进行中', value: 'active' },
      { label: '已完成', value: 'completed' }
    ]
  },
  { key: 'note', label: '备注' }
]

const columns: DataTableColumns<Record<string, unknown>> = [
  { title: '债务名称', key: 'name' },
  { title: '当前余额', key: 'current_balance', align: 'right', render: (row) => money(row.current_balance as string) },
  { title: '年利率', key: 'annual_rate', render: (row) => percent(row.annual_rate as string, 2) },
  {
    title: '计划月还款',
    key: 'payment',
    align: 'right',
    render: (row) => money(Number(row.minimum_monthly_payment || 0) + Number(row.extra_monthly_payment || 0))
  },
  { title: '状态', key: 'status' }
]

const defaults = {
  name: '信用卡分期',
  current_balance: '0',
  annual_rate: '0.1800',
  minimum_monthly_payment: '0',
  extra_monthly_payment: '0',
  status: 'active',
  note: ''
}

const summaryCards = computed(() => {
  if (!progress.value) return []
  return [
    { title: '总债务余额', value: money(progress.value.total_debt_balance) },
    { title: '本月计划还款', value: money(progress.value.planned_monthly_payment) },
    { title: '本月实际还款', value: money(progress.value.actual_debt_payment) },
    { title: '还款完成率', value: percent(progress.value.repayment_completion_rate), tone: 'good' as const }
  ]
})

async function load() {
  loading.value = true
  try {
    const [debtRows, debtProgress] = await Promise.all([
      finance.listDebts({ page_size: 200 }),
      finance.debtProgress(month.value)
    ])
    rows.value = debtRows
    progress.value = debtProgress
  } catch (error) {
    message.error(error instanceof Error ? error.message : '债务加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="metric-grid metric-grid--compact">
    <MetricCard v-for="item in summaryCards" :key="item.title" v-bind="item" />
  </div>
  <DataPanel title="还款月份">
    <n-space>
      <n-input v-model:value="month" class="month-control" placeholder="YYYY-MM" @keyup.enter="load" />
      <n-button @click="load">刷新进度</n-button>
    </n-space>
  </DataPanel>
  <CrudTablePage
    eyebrow="Debt"
    title="债务管理"
    description="记录债务余额、利率和月还款计划，优先处理高息债务。"
    :rows="rows"
    :columns="columns"
    :fields="fields"
    :defaults="defaults"
    :loading="loading"
    create-text="新增债务"
    :on-create="finance.createDebt"
    :on-update="finance.updateDebt"
    :on-delete="finance.deleteDebt"
    @refresh="load"
  />
</template>
