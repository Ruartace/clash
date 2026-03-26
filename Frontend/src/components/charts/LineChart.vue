<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME } from '@/assets/styles/chart-theme'

const props = defineProps<{
  data: { month: string; income: string; expense: string }[]
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function initChart() {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  renderChart()
}

function renderChart() {
  if (!chart) return
  const months = props.data.map((d) => d.month)
  const incomes = props.data.map((d) => parseFloat(d.income))
  const expenses = props.data.map((d) => parseFloat(d.expense))

  chart.setOption({
    ...CHART_THEME,
    tooltip: { ...CHART_THEME.tooltip, trigger: 'axis' },
    legend: { ...CHART_THEME.legend, data: ['收入', '支出'] },
    xAxis: { ...CHART_THEME.categoryAxis, type: 'category', data: months },
    yAxis: { ...CHART_THEME.valueAxis, type: 'value' },
    series: [
      {
        name: '收入',
        type: 'line',
        data: incomes,
        smooth: true,
        itemStyle: { color: '#34d399' },
        areaStyle: { color: 'rgba(52,211,153,0.08)' },
      },
      {
        name: '支出',
        type: 'line',
        data: expenses,
        smooth: true,
        itemStyle: { color: '#f87171' },
        areaStyle: { color: 'rgba(248,113,113,0.08)' },
      },
    ],
  })
}

const resizeObserver = new ResizeObserver(() => chart?.resize())

onMounted(() => {
  initChart()
  if (chartEl.value) resizeObserver.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObserver.disconnect()
  chart?.dispose()
})

watch(() => props.data, renderChart, { deep: true })
</script>

<template>
  <div ref="chartEl" class="chart-container" />
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 300px;
}
</style>
