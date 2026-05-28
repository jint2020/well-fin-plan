<script setup lang="ts">
import { NConfigProvider, NMessageProvider, zhCN, dateZhCN } from 'naive-ui'
import AppShell from './components/AppShell.vue'
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <AppShell v-if="$route.path !== '/login'" />
      <router-view v-else />
    </n-message-provider>
  </n-config-provider>
</template>
