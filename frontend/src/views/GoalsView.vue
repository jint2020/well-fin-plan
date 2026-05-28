<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import CrudTablePage from '../components/CrudTablePage.vue'
import DataPanel from '../components/DataPanel.vue'
import MetricCard from '../components/MetricCard.vue'
import { useFinanceStore } from '../stores/finance'
import type { FinancialGoal, FinancialGoalProgress } from '../types/finance'
import { money, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const rows = ref<FinancialGoal[]>([])
const progress = ref<FinancialGoalProgress | null>(null)
const loading = ref(false)

const fields = [
  { key: 'name', label: '目标名称' },
  {
    key: 'goal_type',
    label: '目标类型',
    type: 'select' as const,
    options: [
      { label: '应急金', value: '应急金' },
      { label: '专项准备金', value: '专项准备金' },
      { label: '长期投资', value: '长期投资' },
      { label: '债务清理', value: '债务清理' }
    ]
  },
  { key: 'target_amount', label: '目标金额' },
  { key: 'current_amount', label: '当前金额' },
  { key: 'monthly_contribution', label: '每月投入' },
  { key: 'target_date', label: '目标日期', type: 'date' as const },
  {
    key: 'status',
    label: '状态',
    type: 'select' as const,
    options: [
      { label: '进行中', value: 'active' },
      { label: '已完成', value: 'completed' }
    ]
  }
]

const columns: DataTableColumns<Record<string, unknown>> = [
  { title: '目标名称', key: 'name' },
  { title: '类型', key: 'goal_type' },
  { title: '目标金额', key: 'target_amount', align: 'right', render: (row) => money(row.target_amount as string) },
  { title: '当前金额', key: 'current_amount', align: 'right', render: (row) => money(row.current_amount as string) },
  { title: '每月投入', key: 'monthly_contribution', align: 'right', render: (row) => money(row.monthly_contribution as string) },
  { title: '状态', key: 'status' }
]

const defaults = {
  name: '长期投资账户',
  goal_type: '长期投资',
  target_amount: '30000',
  current_amount: '0',
  monthly_contribution: '1500',
  target_date: '',
  status: 'active'
}

const overview = computed(() => {
  if (!progress.value) return []
  return [
    { title: '目标总额', value: money(progress.value.total_target_amount) },
    { title: '当前累计', value: money(progress.value.total_current_amount), tone: 'good' as const },
    { title: '整体完成率', value: percent(progress.value.overall_progress_rate), tone: 'warn' as const }
  ]
})

async function load() {
  loading.value = true
  try {
    const [goalRows, goalProgress] = await Promise.all([
      finance.listGoals({ page_size: 200 }),
      finance.goalProgress()
    ])
    rows.value = goalRows
    progress.value = goalProgress
  } catch (error) {
    message.error(error instanceof Error ? error.message : '目标加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="metric-grid metric-grid--compact">
    <MetricCard v-for="item in overview" :key="item.title" v-bind="item" />
  </div>
  <DataPanel title="目标进度">
    <div v-for="item in progress?.items || []" :key="item.id" class="progress-row">
      <span>{{ item.name }}</span>
      <n-progress type="line" :percentage="Number(item.progress_rate) * 100" />
    </div>
  </DataPanel>
  <CrudTablePage
    eyebrow="Goals"
    title="目标计划"
    description="把不定期收入转化为明确的应急金、准备金和长期投资目标。"
    :rows="rows"
    :columns="columns"
    :fields="fields"
    :defaults="defaults"
    :loading="loading"
    create-text="新增目标"
    :on-create="finance.createGoal"
    :on-update="finance.updateGoal"
    :on-delete="finance.deleteGoal"
    @refresh="load"
  />
</template>
