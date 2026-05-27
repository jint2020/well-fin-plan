import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import TransactionsView from '../views/TransactionsView.vue'
import SettingsView from '../views/SettingsView.vue'
import EmergencyFundView from '../views/EmergencyFundView.vue'
import DebtsView from '../views/DebtsView.vue'
import AssetsView from '../views/AssetsView.vue'
import GoalsView from '../views/GoalsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: DashboardView },
    { path: '/transactions', component: TransactionsView },
    { path: '/settings', component: SettingsView },
    { path: '/emergency-fund', component: EmergencyFundView },
    { path: '/debts', component: DebtsView },
    { path: '/assets', component: AssetsView },
    { path: '/goals', component: GoalsView }
  ]
})
