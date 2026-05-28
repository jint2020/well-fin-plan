import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../api/client'
import AssetsView from '../views/AssetsView.vue'
import DashboardView from '../views/DashboardView.vue'
import DebtsView from '../views/DebtsView.vue'
import EmergencyFundView from '../views/EmergencyFundView.vue'
import GoalsView from '../views/GoalsView.vue'
import IncomePlanView from '../views/IncomePlanView.vue'
import LoginView from '../views/LoginView.vue'
import MonthlyBudgetView from '../views/MonthlyBudgetView.vue'
import SettingsView from '../views/SettingsView.vue'
import TransactionsView from '../views/TransactionsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', component: DashboardView },
    { path: '/transactions', component: TransactionsView },
    { path: '/income-plan', component: IncomePlanView },
    { path: '/monthly-budget', component: MonthlyBudgetView },
    { path: '/settings', component: SettingsView },
    { path: '/emergency-fund', component: EmergencyFundView },
    { path: '/debts', component: DebtsView },
    { path: '/assets', component: AssetsView },
    { path: '/goals', component: GoalsView }
  ]
})

router.beforeEach((to) => {
  if (!to.meta.public && !getToken()) {
    return '/login'
  }
  if (to.path === '/login' && getToken()) {
    return '/'
  }
})
