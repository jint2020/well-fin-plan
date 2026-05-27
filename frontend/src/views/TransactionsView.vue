<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const accounts = ref<any[]>([])
const categories = ref<any[]>([])
const rows = ref<any[]>([])
const form = reactive({
  account_id: '',
  category_id: '',
  occurred_on: '2026-01-05',
  amount: '100.00',
  description: ''
})

async function load() {
  accounts.value = await api('/accounts')
  categories.value = await api('/categories')
  rows.value = await api('/transactions')
  if (!form.account_id && accounts.value[0]) form.account_id = accounts.value[0].id
  if (!form.category_id && categories.value[0]) form.category_id = categories.value[0].id
}

async function submit() {
  await api('/transactions', { method: 'POST', body: JSON.stringify(form) })
  await load()
}

onMounted(load)
</script>

<template>
  <section class="panel">
    <h2>流水记录</h2>
    <el-form inline>
      <el-form-item label="账户">
        <el-select v-model="form.account_id" class="select">
          <el-option v-for="item in accounts" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category_id" class="select">
          <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期"><el-input v-model="form.occurred_on" /></el-form-item>
      <el-form-item label="金额"><el-input v-model="form.amount" /></el-form-item>
      <el-button type="primary" @click="submit">新增</el-button>
    </el-form>
  </section>
  <el-table :data="rows" class="table">
    <el-table-column prop="occurred_on" label="日期" />
    <el-table-column prop="transaction_type" label="类型" />
    <el-table-column prop="amount" label="金额" />
    <el-table-column prop="description" label="说明" />
  </el-table>
</template>
