<script setup lang="ts">
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps<{
  option: echarts.EChartsOption
  height?: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

async function render() {
  await nextTick()
  if (!chartEl.value) return
  if (!chart) {
    chart = echarts.init(chartEl.value)
    window.addEventListener('resize', resize)
  }
  chart.setOption(props.option, true)
}

function resize() {
  chart?.resize()
}

watch(() => props.option, render, { deep: true, immediate: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="chartEl" class="finance-chart" :style="{ height: `${height ?? 320}px` }" />
</template>
