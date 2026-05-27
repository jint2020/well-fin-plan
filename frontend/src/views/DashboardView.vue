<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { api } from '../api/client'

const data = ref<any>(null)
const month = ref('2026-01')
const chartEl = ref<HTMLDivElement | null>(null)

async function load() {
  data.value = await api(`/dashboard/monthly?month=${month.value}`)
  await nextTick()
  renderChart()
}

function renderChart() {
  if (!chartEl.value || !data.value) return
  const budget = data.value.monthly_budget
  const chart = echarts.init(chartEl.value)
  chart.setOption({
    tooltip: {},
    xAxis: { type: 'category', data: ['必要', '储蓄/还债', '准备金', '弹性'] },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: [
          Number(budget.necessary_budget),
          Number(budget.recommended_saving_debt),
          Number(budget.recommended_reserve),
          Number(budget.recommended_flex)
        ],
        itemStyle: { color: '#409eff' }
      }
    ]
  })
}

onMounted(load)
</script>

<template>
  <section class="toolbar">
    <h2>月度仪表盘</h2>
    <el-input v-model="month" class="month-input" @change="load" />
  </section>
  <section v-if="data" class="metrics">
    <el-statistic title="工资收入" :value="Number(data.monthly_budget.salary_income)" />
    <el-statistic title="非工资收入" :value="Number(data.monthly_budget.non_salary_income)" />
    <el-statistic title="额外收入" :value="Number(data.monthly_budget.extra_income)" />
    <el-statistic title="本月结余" :value="Number(data.monthly_budget.monthly_surplus)" />
  </section>
  <section v-if="data" class="panel">
    <h3>建议预算分配</h3>
    <div ref="chartEl" class="chart"></div>
  </section>
  <el-empty v-else description="请先登录并录入流水" />
</template>
