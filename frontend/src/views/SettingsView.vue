<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { api } from '../api/client'

const form = reactive<Record<string, string>>({
  salary_min: '',
  salary_max: '',
  conservative_income_base: '',
  necessity_ratio: '',
  saving_ratio: '',
  flex_ratio: '',
  extra_saving_ratio: '',
  extra_reserve_ratio: '',
  extra_flex_ratio: '',
  emergency_months: '',
  monthly_necessity_amount: '',
  plan_year: ''
})

async function load() {
  const data = await api<Record<string, string | number>>('/settings')
  for (const key of Object.keys(form)) form[key] = String(data[key] ?? '')
}

async function save() {
  await api('/settings', { method: 'PUT', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>参数设置</h2>
    <el-form label-position="top" class="settings-grid">
      <el-form-item v-for="(_, key) in form" :key="key" :label="key">
        <el-input v-model="form[key]" />
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="save">保存</el-button>
  </section>
</template>
