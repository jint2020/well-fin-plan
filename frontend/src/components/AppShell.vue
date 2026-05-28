<script setup lang="ts">
import {
  BarChart3,
  CalendarRange,
  CreditCard,
  FileText,
  Flag,
  Landmark,
  LayoutDashboard,
  LogOut,
  PieChart,
  Settings,
  ShieldCheck,
  Wallet
} from 'lucide-vue-next'
import type { LucideIcon } from 'lucide-vue-next'
import { computed, h, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { NButton, NLayout, NLayoutContent, NLayoutHeader, NLayoutSider, NMenu, NSpace, NTag } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const menuOptions = [
  { label: '仪表盘', key: '/', icon: icon(LayoutDashboard) },
  { label: '流水记录', key: '/transactions', icon: icon(FileText) },
  { label: '收入规划', key: '/income-plan', icon: icon(CalendarRange) },
  { label: '月度预算', key: '/monthly-budget', icon: icon(BarChart3) },
  { label: '应急金', key: '/emergency-fund', icon: icon(ShieldCheck) },
  { label: '债务管理', key: '/debts', icon: icon(CreditCard) },
  { label: '资产配置', key: '/assets', icon: icon(PieChart) },
  { label: '目标计划', key: '/goals', icon: icon(Flag) },
  { label: '参数设置', key: '/settings', icon: icon(Settings) }
]

const activeKey = computed(() => route.path)

function icon(component: LucideIcon) {
  return () => h(component, { size: 18, strokeWidth: 1.8 })
}

function navigate(key: string) {
  router.push(key)
}

async function logout() {
  await auth.logout()
  router.push('/login')
}

onMounted(() => {
  auth.loadMe().catch(() => undefined)
})
</script>

<template>
  <n-layout has-sider class="admin-shell">
    <n-layout-sider :width="252" bordered class="admin-sidebar">
      <div class="brand">
        <div class="brand__mark"><Landmark :size="24" /></div>
        <div>
          <strong>Well Fin Plan</strong>
          <span>个人资金管理</span>
        </div>
      </div>
      <n-menu :value="activeKey" :options="menuOptions" @update:value="navigate" />
    </n-layout-sider>

    <n-layout>
      <n-layout-header bordered class="topbar">
        <div>
          <span class="topbar__caption">现金流 → 应急金 → 风险保障 → 债务 → 投资 → 配置</span>
        </div>
        <n-space align="center">
          <n-tag round size="small" type="success">{{ auth.user?.email || '已登录' }}</n-tag>
          <n-button quaternary size="small" @click="logout">
            <template #icon><LogOut :size="16" /></template>
            退出
          </n-button>
        </n-space>
      </n-layout-header>
      <n-layout-content class="admin-content">
        <RouterView />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>
