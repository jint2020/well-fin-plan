<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const rows = ref<any[]>([])
const form = reactive({ name: '信用卡分期', current_balance: '0', annual_rate: '0.18' })

async function load() {
  rows.value = await api('/debts')
}

async function submit() {
  await api('/debts', { method: 'POST', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>债务管理</h2>
    <el-form inline>
      <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="余额"><el-input v-model="form.current_balance" /></el-form-item>
      <el-form-item label="年利率"><el-input v-model="form.annual_rate" /></el-form-item>
      <el-button type="primary" @click="submit">新增</el-button>
    </el-form>
  </section>
  <el-table :data="rows">
    <el-table-column prop="name" label="债务名称" />
    <el-table-column prop="current_balance" label="当前余额" />
    <el-table-column prop="annual_rate" label="年利率" />
    <el-table-column prop="status" label="状态" />
  </el-table>
</template>
