<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const rows = ref<any[]>([])
const form = reactive({
  name: '长期投资账户',
  goal_type: '长期投资',
  target_amount: '30000',
  current_amount: '6000',
  monthly_contribution: '1500'
})

async function load() {
  rows.value = await api('/goals')
}

async function submit() {
  await api('/goals', { method: 'POST', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>目标计划</h2>
    <el-form inline>
      <el-form-item label="目标"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="类型"><el-input v-model="form.goal_type" /></el-form-item>
      <el-form-item label="目标金额"><el-input v-model="form.target_amount" /></el-form-item>
      <el-form-item label="当前金额"><el-input v-model="form.current_amount" /></el-form-item>
      <el-button type="primary" @click="submit">新增</el-button>
    </el-form>
  </section>
  <el-table :data="rows">
    <el-table-column prop="name" label="目标名称" />
    <el-table-column prop="goal_type" label="类型" />
    <el-table-column prop="target_amount" label="目标金额" />
    <el-table-column prop="current_amount" label="当前金额" />
    <el-table-column prop="status" label="状态" />
  </el-table>
</template>
