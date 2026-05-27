<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import DataPanel from '../components/DataPanel.vue'
import PageHeader from '../components/PageHeader.vue'
import { useFinanceStore } from '../stores/finance'
import type { Settings } from '../types/finance'

const finance = useFinanceStore()
const message = useMessage()
const saving = ref(false)
const form = reactive<Record<keyof Settings, string | number>>({
  salary_min: '',
  salary_max: '',
  conservative_income_base: '',
  necessity_ratio: '',
  saving_ratio: '',
  flex_ratio: '',
  extra_saving_ratio: '',
  extra_reserve_ratio: '',
  extra_flex_ratio: '',
  emergency_months: 3,
  monthly_necessity_amount: '',
  plan_year: new Date().getFullYear()
})

const groups = [
  {
    title: '收入基准',
    fields: [
      ['salary_min', '工资收入下限'],
      ['salary_max', '工资收入上限'],
      ['conservative_income_base', '保守预算基准'],
      ['plan_year', '年度']
    ]
  },
  {
    title: '基础预算比例',
    fields: [
      ['necessity_ratio', '必要支出比例'],
      ['saving_ratio', '储蓄/投资/还债比例'],
      ['flex_ratio', '弹性消费比例']
    ]
  },
  {
    title: '额外收入分配',
    fields: [
      ['extra_saving_ratio', '额外收入→储蓄/投资/还债'],
      ['extra_reserve_ratio', '额外收入→专项准备金'],
      ['extra_flex_ratio', '额外收入→弹性消费']
    ]
  },
  {
    title: '应急金',
    fields: [
      ['emergency_months', '目标月数'],
      ['monthly_necessity_amount', '每月必要生活费']
    ]
  }
] as const

async function load() {
  try {
    const data = await finance.loadSettings()
    for (const key of Object.keys(form) as (keyof Settings)[]) {
      form[key] = data[key] as string | number
    }
  } catch (error) {
    message.error(error instanceof Error ? error.message : '参数加载失败')
  }
}

async function save() {
  saving.value = true
  try {
    await finance.saveSettings({
      ...form,
      emergency_months: Number(form.emergency_months),
      plan_year: Number(form.plan_year)
    })
    message.success('参数已保存')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <PageHeader
    eyebrow="Settings"
    title="参数设置"
    description="维护保守收入基准、50/30/20 预算比例、额外收入分配和应急金目标。"
  >
    <template #actions>
      <n-button type="primary" :loading="saving" @click="save">保存参数</n-button>
    </template>
  </PageHeader>

  <div class="settings-layout">
    <DataPanel v-for="group in groups" :key="group.title" :title="group.title">
      <n-form label-placement="top" class="settings-grid">
        <n-form-item v-for="[key, label] in group.fields" :key="key" :label="label">
          <n-input v-model:value="form[key]" />
        </n-form-item>
      </n-form>
    </DataPanel>
  </div>
</template>
