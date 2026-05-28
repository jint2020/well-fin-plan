export type DecimalValue = string | number

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserProfile {
  id: string
  email: string
  display_name: string | null
}

export interface Account {
  id: string
  name: string
  account_type: string
  is_active: boolean
}

export interface Category {
  id: string
  name: string
  transaction_type: string
  is_income: boolean
  is_salary: boolean
  sort_order: number
}

export interface Transaction {
  id: string
  account_id: string
  category_id: string
  occurred_on: string
  month: string
  transaction_type: string
  counterparty: string | null
  recurrence_type: string | null
  description: string | null
  amount: DecimalValue
  note: string | null
}

export interface TransactionPayload {
  account_id: string
  category_id: string
  occurred_on: string
  amount: DecimalValue
  counterparty?: string | null
  recurrence_type?: string | null
  description?: string | null
  note?: string | null
}

export interface Settings {
  salary_min: DecimalValue
  salary_max: DecimalValue
  conservative_income_base: DecimalValue
  necessity_ratio: DecimalValue
  saving_ratio: DecimalValue
  flex_ratio: DecimalValue
  extra_saving_ratio: DecimalValue
  extra_reserve_ratio: DecimalValue
  extra_flex_ratio: DecimalValue
  emergency_months: number
  monthly_necessity_amount: DecimalValue
  plan_year: number
}

export interface MonthlyBudget {
  month: string
  salary_income: DecimalValue
  non_salary_income: DecimalValue
  actual_total_income: DecimalValue
  budget_income: DecimalValue
  necessary_budget: DecimalValue
  base_saving_budget: DecimalValue
  base_flex_budget: DecimalValue
  extra_income: DecimalValue
  extra_to_saving_debt: DecimalValue
  extra_to_reserve: DecimalValue
  extra_to_flex: DecimalValue
  recommended_saving_debt: DecimalValue
  recommended_reserve: DecimalValue
  recommended_flex: DecimalValue
  actual_necessary: DecimalValue
  actual_saving_investment: DecimalValue
  actual_flex: DecimalValue
  actual_debt_payment: DecimalValue
  actual_reserve: DecimalValue
  monthly_surplus: DecimalValue
  saving_debt_rate: DecimalValue
  status: string
}

export interface MonthlyIncomeSummary {
  month: string
  salary_income: DecimalValue
  non_salary_income: DecimalValue
  total_income: DecimalValue
  by_category: Record<string, DecimalValue>
}

export interface MonthlyExpenseSummary {
  month: string
  total_expense: DecimalValue
  by_type: Record<string, DecimalValue>
  by_category: Record<string, DecimalValue>
}

export interface EmergencyFundPlan {
  id: string
  month: string
  planned_amount: DecimalValue
  opening_balance: DecimalValue
  note: string | null
}

export interface EmergencyFundProgress {
  month: string
  target_amount: DecimalValue
  planned_amount: DecimalValue
  actual_month_deposit: DecimalValue
  current_amount: DecimalValue
  progress_rate: DecimalValue
  remaining_amount: DecimalValue
}

export interface Debt {
  id: string
  name: string
  current_balance: DecimalValue
  annual_rate: DecimalValue
  minimum_monthly_payment: DecimalValue
  extra_monthly_payment: DecimalValue
  status: string
  note: string | null
}

export interface DebtProgressItem extends Debt {
  monthly_payment_plan: DecimalValue
  monthly_payment_progress_rate: DecimalValue | null
}

export interface DebtProgress {
  month: string
  total_debt_balance: DecimalValue
  planned_monthly_payment: DecimalValue
  actual_debt_payment: DecimalValue
  repayment_completion_rate: DecimalValue
  items: DebtProgressItem[]
}

export interface AssetAllocation {
  id: string
  asset_class: string
  current_amount: DecimalValue
  target_ratio: DecimalValue
  risk_level: string | null
  note: string | null
}

export interface AssetAllocationSummaryItem extends AssetAllocation {
  current_ratio: DecimalValue
  target_amount: DecimalValue
  gap_amount: DecimalValue
}

export interface AssetAllocationSummary {
  total_amount: DecimalValue
  items: AssetAllocationSummaryItem[]
}

export interface FinancialGoal {
  id: string
  name: string
  goal_type: string
  target_amount: DecimalValue
  current_amount: DecimalValue
  monthly_contribution: DecimalValue
  target_date: string | null
  status: string
}

export interface FinancialGoalProgressItem extends FinancialGoal {
  progress_rate: DecimalValue
  remaining_amount: DecimalValue
}

export interface FinancialGoalProgress {
  total_target_amount: DecimalValue
  total_current_amount: DecimalValue
  overall_progress_rate: DecimalValue
  items: FinancialGoalProgressItem[]
}

export interface DashboardSummary {
  monthly_budget: MonthlyBudget
  income_summary: MonthlyIncomeSummary
  expense_summary: MonthlyExpenseSummary
  emergency_fund_progress: EmergencyFundProgress
  debt_progress: DebtProgress
  asset_allocation_summary: AssetAllocationSummary
  goal_progress: FinancialGoalProgress
  net_assets: DecimalValue
  debt_balance: DecimalValue
  emergency_fund_balance: DecimalValue
}

export interface IncomePlan {
  year: number
  months: MonthlyBudget[]
}
