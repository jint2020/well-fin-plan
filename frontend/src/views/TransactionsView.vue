<script setup lang="ts">
import type { DataTableColumns } from 'naive-ui'
import { computed, onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import CrudTablePage from '../components/CrudTablePage.vue'
import { useFinanceStore } from '../stores/finance'
import type { Transaction, TransactionPayload } from '../types/finance'
import { currentMonth, money } from '../utils/format'

const finance = useFinanceStore()
const message = useMessage()
const rows = ref<Transaction[]>([])
const loading = ref(false)
const filters = reactive({ month: currentMonth(), transaction_type: '', category_id: '' })

const accountOptions = computed(() => finance.accounts.map((item) => ({ label: item.name, value: item.id })))
const categoryOptions = computed(() => finance.categories.map((item) => ({ label: `${item.name} · ${item.transaction_type}`, value: item.id })))
const typeOptions = computed(() => [...new Set(finance.categories.map((item) => item.transaction_type))].map((item) => ({ label: item, value: item })))

const fields = computed(() => [
  { key: 'account_id', label: '账户', type: 'select' as const, options: accountOptions.value },
  { key: 'category_id', label: '分类', type: 'select' as const, options: categoryOptions.value },
  { key: 'occurred_on', label: '日期', type: 'date' as const, placeholder: '2026-01-05' },
  { key: 'amount', label: '金额' },
  { key: 'counterparty', label: '对方/来源' },
  { key: 'description', label: '说明' },
  { key: 'note', label: '备注' }
])

const columns: DataTableColumns<Record<string, unknown>> = [
  { title: '日期', key: 'occurred_on', width: 110 },
  { title: '类型', key: 'transaction_type', width: 100 },
  {
    title: '账户',
    key: 'account_id',
    render: (row) => finance.accountById.get(String(row.account_id))?.name || '-'
  },
  {
    title: '分类',
    key: 'category_id',
    render: (row) => finance.categoryById.get(String(row.category_id))?.name || '-'
  },
  { title: '金额', key: 'amount', align: 'right', render: (row) => money(row.amount as string) },
  { title: '说明', key: 'description', ellipsis: { tooltip: true } }
]

const defaults = computed(() => ({
  account_id: finance.accounts[0]?.id || '',
  category_id: finance.categories[0]?.id || '',
  occurred_on: `${filters.month}-05`,
  amount: '100.00',
  counterparty: '',
  description: '',
  note: ''
}))

async function load() {
  loading.value = true
  try {
    await finance.loadReferenceData()
    rows.value = await finance.listTransactions({
      month: filters.month || undefined,
      transaction_type: filters.transaction_type || undefined,
      category_id: filters.category_id || undefined,
      page_size: 200
    })
  } catch (error) {
    message.error(error instanceof Error ? error.message : '流水加载失败')
  } finally {
    loading.value = false
  }
}

async function create(payload: Record<string, unknown>) {
  await finance.createTransaction(payload as unknown as TransactionPayload)
}

async function update(id: string, payload: Record<string, unknown>) {
  await finance.updateTransaction(id, payload as Partial<TransactionPayload>)
}

async function remove(id: string) {
  await finance.deleteTransaction(id)
}

onMounted(load)
</script>

<template>
  <CrudTablePage
    eyebrow="Cash Flow"
    title="流水记录"
    description="记录工资、非工资收入、必要支出、储蓄投资、还债和弹性消费。"
    :rows="rows"
    :columns="columns"
    :fields="fields"
    :defaults="defaults"
    :loading="loading"
    create-text="新增流水"
    :on-create="create"
    :on-update="update"
    :on-delete="remove"
    @refresh="load"
  >
    <template #filters>
      <n-space align="center">
        <n-input v-model:value="filters.month" class="month-control" placeholder="YYYY-MM" @keyup.enter="load" />
        <n-select v-model:value="filters.transaction_type" clearable class="filter-control" :options="typeOptions" placeholder="类型" />
        <n-select v-model:value="filters.category_id" clearable filterable class="filter-control" :options="categoryOptions" placeholder="分类" />
        <n-button @click="load">筛选</n-button>
      </n-space>
    </template>
  </CrudTablePage>
</template>
