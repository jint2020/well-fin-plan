import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { http } from '../api/client'
import { currentMonth } from '../utils/format'
import type {
  Account,
  AssetAllocation,
  AssetAllocationSummary,
  DashboardSummary,
  Debt,
  DebtProgress,
  EmergencyFundPlan,
  EmergencyFundProgress,
  FinancialGoal,
  FinancialGoalProgress,
  IncomePlan,
  MonthlyBudget,
  Settings,
  Transaction,
  TransactionPayload,
  Category
} from '../types/finance'

type ListParams = Record<string, string | number | undefined>

export const useFinanceStore = defineStore('finance', () => {
  const activeMonth = ref(currentMonth())
  const accounts = ref<Account[]>([])
  const categories = ref<Category[]>([])
  const dashboard = ref<DashboardSummary | null>(null)
  const loading = ref(false)

  const categoryById = computed(() => new Map(categories.value.map((item) => [item.id, item])))
  const accountById = computed(() => new Map(accounts.value.map((item) => [item.id, item])))

  async function loadReferenceData() {
    const [accountResponse, categoryResponse] = await Promise.all([
      http.get<Account[]>('/accounts'),
      http.get<Category[]>('/categories')
    ])
    accounts.value = accountResponse.data
    categories.value = categoryResponse.data
  }

  async function loadDashboard(month = activeMonth.value) {
    loading.value = true
    try {
      activeMonth.value = month
      const { data } = await http.get<DashboardSummary>('/dashboard/monthly', { params: { month } })
      dashboard.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function listTransactions(params: ListParams = {}) {
    const { data } = await http.get<Transaction[]>('/transactions', { params })
    return data
  }

  async function createTransaction(payload: TransactionPayload) {
    const { data } = await http.post<Transaction>('/transactions', payload)
    return data
  }

  async function updateTransaction(id: string, payload: Partial<TransactionPayload>) {
    const { data } = await http.patch<Transaction>(`/transactions/${id}`, payload)
    return data
  }

  async function deleteTransaction(id: string) {
    await http.delete(`/transactions/${id}`)
  }

  async function loadSettings() {
    const { data } = await http.get<Settings>('/settings')
    return data
  }

  async function saveSettings(payload: Partial<Settings>) {
    const { data } = await http.patch<Settings>('/settings', payload)
    return data
  }

  async function monthlyBudget(month = activeMonth.value) {
    const { data } = await http.get<MonthlyBudget>('/reports/monthly-budget', { params: { month } })
    return data
  }

  async function incomePlan(year: number) {
    const { data } = await http.get<IncomePlan>('/reports/income-plan', { params: { year } })
    return data
  }

  async function listEmergencyPlans(params: ListParams = {}) {
    const { data } = await http.get<EmergencyFundPlan[]>('/emergency-fund/plans', { params })
    return data
  }

  async function emergencyProgress(month = activeMonth.value) {
    const { data } = await http.get<EmergencyFundProgress>('/emergency-fund/progress', { params: { month } })
    return data
  }

  async function createEmergencyPlan(payload: Partial<EmergencyFundPlan>) {
    const { data } = await http.post<EmergencyFundPlan>('/emergency-fund/plans', payload)
    return data
  }

  async function updateEmergencyPlan(id: string, payload: Partial<EmergencyFundPlan>) {
    const { data } = await http.patch<EmergencyFundPlan>(`/emergency-fund/plans/${id}`, payload)
    return data
  }

  async function deleteEmergencyPlan(id: string) {
    await http.delete(`/emergency-fund/plans/${id}`)
  }

  async function listDebts(params: ListParams = {}) {
    const { data } = await http.get<Debt[]>('/debts', { params })
    return data
  }

  async function debtProgress(month = activeMonth.value) {
    const { data } = await http.get<DebtProgress>('/debts/progress', { params: { month } })
    return data
  }

  async function createDebt(payload: Partial<Debt>) {
    const { data } = await http.post<Debt>('/debts', payload)
    return data
  }

  async function updateDebt(id: string, payload: Partial<Debt>) {
    const { data } = await http.patch<Debt>(`/debts/${id}`, payload)
    return data
  }

  async function deleteDebt(id: string) {
    await http.delete(`/debts/${id}`)
  }

  async function listAssets(params: ListParams = {}) {
    const { data } = await http.get<AssetAllocation[]>('/asset-allocations', { params })
    return data
  }

  async function assetSummary() {
    const { data } = await http.get<AssetAllocationSummary>('/asset-allocations/summary')
    return data
  }

  async function createAsset(payload: Partial<AssetAllocation>) {
    const { data } = await http.post<AssetAllocation>('/asset-allocations', payload)
    return data
  }

  async function updateAsset(id: string, payload: Partial<AssetAllocation>) {
    const { data } = await http.patch<AssetAllocation>(`/asset-allocations/${id}`, payload)
    return data
  }

  async function deleteAsset(id: string) {
    await http.delete(`/asset-allocations/${id}`)
  }

  async function listGoals(params: ListParams = {}) {
    const { data } = await http.get<FinancialGoal[]>('/goals', { params })
    return data
  }

  async function goalProgress() {
    const { data } = await http.get<FinancialGoalProgress>('/goals/progress')
    return data
  }

  async function createGoal(payload: Partial<FinancialGoal>) {
    const { data } = await http.post<FinancialGoal>('/goals', payload)
    return data
  }

  async function updateGoal(id: string, payload: Partial<FinancialGoal>) {
    const { data } = await http.patch<FinancialGoal>(`/goals/${id}`, payload)
    return data
  }

  async function deleteGoal(id: string) {
    await http.delete(`/goals/${id}`)
  }

  return {
    activeMonth,
    accounts,
    categories,
    dashboard,
    loading,
    categoryById,
    accountById,
    loadReferenceData,
    loadDashboard,
    listTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    loadSettings,
    saveSettings,
    monthlyBudget,
    incomePlan,
    listEmergencyPlans,
    emergencyProgress,
    createEmergencyPlan,
    updateEmergencyPlan,
    deleteEmergencyPlan,
    listDebts,
    debtProgress,
    createDebt,
    updateDebt,
    deleteDebt,
    listAssets,
    assetSummary,
    createAsset,
    updateAsset,
    deleteAsset,
    listGoals,
    goalProgress,
    createGoal,
    updateGoal,
    deleteGoal
  }
})
