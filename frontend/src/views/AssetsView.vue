<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import type { EChartsOption } from 'echarts'
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import CrudTablePage from '../components/CrudTablePage.vue'
import DataPanel from '../components/DataPanel.vue'
import FinanceChart from '../components/FinanceChart.vue'
import MetricCard from '../components/MetricCard.vue'
import { useFinanceStore } from '../stores/finance'
import type { AssetAllocation, AssetAllocationSummary } from '../types/finance'
import { money, numberValue, percent } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const rows = ref<AssetAllocation[]>([])
const summary = ref<AssetAllocationSummary | null>(null)
const loading = ref(false)

const fields = [
  { key: 'asset_class', label: '资产类别' },
  { key: 'current_amount', label: '当前金额' },
  { key: 'target_ratio', label: '目标比例' },
  {
    key: 'risk_level',
    label: '风险等级',
    type: 'select' as const,
    options: [
      { label: '保守', value: '保守' },
      { label: '平衡', value: '平衡' },
      { label: '进取', value: '进取' }
    ]
  },
  { key: 'note', label: '备注' }
]

const columns: DataTableColumns<Record<string, unknown>> = [
  { title: '资产类别', key: 'asset_class' },
  { title: '当前金额', key: 'current_amount', align: 'right', render: (row) => money(row.current_amount as string) },
  { title: '目标比例', key: 'target_ratio', render: (row) => percent(row.target_ratio as string) },
  { title: '风险等级', key: 'risk_level' },
  { title: '备注', key: 'note', ellipsis: { tooltip: true } }
]

const defaults = {
  asset_class: '权益基金/股票',
  current_amount: '0',
  target_ratio: '0.3500',
  risk_level: '平衡',
  note: ''
}

const chartOption = computed<EChartsOption>(() => ({
  color: ['#cc785c', '#5db8a6', '#e8a55a', '#5db872', '#8e8b82'],
  tooltip: { trigger: 'item' },
  series: [
    {
      type: 'pie',
      radius: ['45%', '72%'],
      data:
        summary.value?.items.map((item) => ({
          name: item.asset_class,
          value: numberValue(item.current_amount)
        })) ?? []
    }
  ]
}))

async function load() {
  loading.value = true
  try {
    const [assetRows, assetSummary] = await Promise.all([
      finance.listAssets({ page_size: 200 }),
      finance.assetSummary()
    ])
    rows.value = assetRows
    summary.value = assetSummary
  } catch (error) {
    message.error(error instanceof Error ? error.message : '资产加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="dashboard-grid">
    <MetricCard title="资产总额" :value="money(summary?.total_amount)" />
    <DataPanel title="当前资产占比">
      <FinanceChart :option="chartOption" :height="260" />
    </DataPanel>
  </div>
  <CrudTablePage
    eyebrow="Allocation"
    title="资产配置"
    description="维护资产类别、当前金额和目标比例，跟踪再平衡差额。"
    :rows="rows"
    :columns="columns"
    :fields="fields"
    :defaults="defaults"
    :loading="loading"
    create-text="新增资产"
    :on-create="finance.createAsset"
    :on-update="finance.updateAsset"
    :on-delete="finance.deleteAsset"
    @refresh="load"
  />
</template>
