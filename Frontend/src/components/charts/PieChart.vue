<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_THEME, CHART_COLORS } from '@/assets/styles/chart-theme'

const props = defineProps<{
  data: { name: string; value: number }[]
  title?: string
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
  chart.setOption({
    ...CHART_THEME,
    tooltip: { ...CHART_THEME.tooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { ...CHART_THEME.legend, orient: 'vertical', right: '5%', top: 'center' },
    series: [
      {
        name: props.title ?? '分布',
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['38%', '50%'],
        data: props.data,
        color: CHART_COLORS.palette,
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.4)' },
        },
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
  height: 280px;
}
</style>
