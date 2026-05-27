<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const rows = ref<any[]>([])
const form = reactive({ asset_class: '权益基金/股票', current_amount: '6000', target_ratio: '0.35' })

async function load() {
  rows.value = await api('/asset-allocations')
}

async function submit() {
  await api('/asset-allocations', { method: 'POST', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>资产配置</h2>
    <el-form inline>
      <el-form-item label="资产类别"><el-input v-model="form.asset_class" /></el-form-item>
      <el-form-item label="当前金额"><el-input v-model="form.current_amount" /></el-form-item>
      <el-form-item label="目标比例"><el-input v-model="form.target_ratio" /></el-form-item>
      <el-button type="primary" @click="submit">新增</el-button>
    </el-form>
  </section>
  <el-table :data="rows">
    <el-table-column prop="asset_class" label="资产类别" />
    <el-table-column prop="current_amount" label="当前金额" />
    <el-table-column prop="target_ratio" label="目标比例" />
  </el-table>
</template>
