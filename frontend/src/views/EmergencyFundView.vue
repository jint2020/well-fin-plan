<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import CrudTablePage from '../components/CrudTablePage.vue'
import DataPanel from '../components/DataPanel.vue'
import MetricCard from '../components/MetricCard.vue'
import { useFinanceStore } from '../stores/finance'
import type { EmergencyFundPlan, EmergencyFundProgress } from '../types/finance'
import { currentMonth, money, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const rows = ref<EmergencyFundPlan[]>([])
const progress = ref<EmergencyFundProgress | null>(null)
const month = ref(currentMonth())
const loading = ref(false)

const fields = [
  { key: 'month', label: '月份', type: 'date' as const, placeholder: '2026-01-01' },
  { key: 'planned_amount', label: '计划存入' },
  { key: 'opening_balance', label: '期初余额' },
  { key: 'note', label: '备注' }
]

const columns: DataTableColumns<Record<string, unknown>> = [
  { title: '月份', key: 'month' },
  { title: '计划存入', key: 'planned_amount', align: 'right', render: (row) => money(row.planned_amount as string) },
  { title: '期初余额', key: 'opening_balance', align: 'right', render: (row) => money(row.opening_balance as string) },
  { title: '备注', key: 'note', ellipsis: { tooltip: true } }
]

const defaults = computed(() => ({
  month: `${month.value}-01`,
  planned_amount: '900',
  opening_balance: '0',
  note: ''
}))

async function load() {
  loading.value = true
  try {
    const [plans, fundProgress] = await Promise.all([
      finance.listEmergencyPlans({ page_size: 200 }),
      finance.emergencyProgress(month.value)
    ])
    rows.value = plans
    progress.value = fundProgress
  } catch (error) {
    message.error(error instanceof Error ? error.message : '应急金加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <DataPanel title="查看月份">
    <n-space>
      <n-input v-model:value="month" class="month-control" placeholder="YYYY-MM" @keyup.enter="load" />
      <n-button @click="load">刷新进度</n-button>
    </n-space>
  </DataPanel>
  <div class="metric-grid metric-grid--compact">
    <MetricCard title="目标金额" :value="money(progress?.target_amount)" />
    <MetricCard title="当前余额" :value="money(progress?.current_amount)" tone="good" />
    <MetricCard title="本月计划" :value="money(progress?.planned_amount)" />
    <MetricCard title="达成率" :value="percent(progress?.progress_rate)" tone="warn" />
  </div>
  <CrudTablePage
    eyebrow="Emergency"
    title="应急金"
    description="先补足安全垫，再扩大高波动投资。期初余额加本月实际存入构成本月应急金余额。"
    :rows="rows"
    :columns="columns"
    :fields="fields"
    :defaults="defaults"
    :loading="loading"
    create-text="新增计划"
    :on-create="finance.createEmergencyPlan"
    :on-update="finance.updateEmergencyPlan"
    :on-delete="finance.deleteEmergencyPlan"
    @refresh="load"
  />
</template>
