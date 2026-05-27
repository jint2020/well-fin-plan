<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const rows = ref<any[]>([])
const form = reactive({ month: '2026-01-01', planned_amount: '900', opening_balance: '0', note: '' })

async function load() {
  rows.value = await api('/emergency-fund/plans')
}

async function submit() {
  await api('/emergency-fund/plans', { method: 'POST', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>应急金计划</h2>
    <el-form inline>
      <el-form-item label="月份"><el-input v-model="form.month" /></el-form-item>
      <el-form-item label="计划存入"><el-input v-model="form.planned_amount" /></el-form-item>
      <el-form-item label="期初余额"><el-input v-model="form.opening_balance" /></el-form-item>
      <el-button type="primary" @click="submit">新增</el-button>
    </el-form>
  </section>
  <el-table :data="rows">
    <el-table-column prop="month" label="月份" />
    <el-table-column prop="planned_amount" label="计划存入" />
    <el-table-column prop="opening_balance" label="期初余额" />
    <el-table-column prop="note" label="备注" />
  </el-table>
</template>
