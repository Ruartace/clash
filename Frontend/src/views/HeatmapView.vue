<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import * as echarts from 'echarts'

import { getHeatmapData } from '@/api/statistics'
import type { HeatmapMode, HeatmapPoint } from '@/types'
import { CHART_COLORS } from '@/assets/styles/chart-theme'

const loading = ref(false)
const visible = ref(false)

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const years = [currentYear - 2, currentYear - 1, currentYear]
const mode = ref<HeatmapMode>('expense')

const data = ref<HeatmapPoint[]>([])

const chartEl = ref<HTMLDivElement | null>(null)
const chart = shallowRef<echarts.ECharts>()

const maxVal = computed(() => {
  if (!data.value.length) return 1
  return Math.max(...data.value.map((d) => Math.abs(d.value)))
})

const summaryStats = computed(() => {
  const total = data.value.reduce((s, d) => s + d.value, 0)
  const activeDays = data.value.filter((d) => d.value !== 0).length
  const peak = data.value.reduce((a, b) => (Math.abs(b.value) > Math.abs(a.value) ? b : a), { date: '-', value: 0 })
  return { total, activeDays, peak }
})

function buildOption(): echarts.EChartsOption {
  const isNet = mode.value === 'net'
  const isIncome = mode.value === 'income'
  const colorRange: string[] = isNet
    ? [CHART_COLORS.expense, '#2e2b27', CHART_COLORS.income]
    : isIncome
      ? ['#1e2e24', CHART_COLORS.income]
      : ['#1e1d1b', CHART_COLORS.expense]

  return {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: '#1e1d1b',
      borderColor: '#2e2b27',
      textStyle: { color: '#bfbebf', fontFamily: "'DM Sans', sans-serif", fontSize: 12 },
      formatter: (p: any) => {
        const val = Number(p.value[1] || 0)
        const sign = val >= 0 ? '' : '-'
        const abs = Math.abs(val)
        return `<b style="color:#bfbebf">${p.value[0]}</b><br/><span style="color:${val >= 0 ? CHART_COLORS.income : CHART_COLORS.expense}">${sign}¥${abs.toLocaleString('zh-CN')}</span>`
      },
    },
    visualMap: {
      min: isNet ? -maxVal.value : 0,
      max: maxVal.value,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: colorRange },
      textStyle: { color: '#7a7874', fontSize: 11 },
    },
    calendar: {
      top: 72,
      left: 30,
      right: 20,
      bottom: 50,
      range: selectedYear.value,
      itemStyle: { color: '#171716', borderColor: '#252320', borderWidth: 2 },
      dayLabel: { color: '#7a7874', fontSize: 10, nameMap: ['日', '一', '二', '三', '四', '五', '六'] },
      monthLabel: { color: '#bfbebf', fontSize: 11 },
      yearLabel: { show: false },
      splitLine: { show: true, lineStyle: { color: '#2e2b27', width: 1 } },
    },
    series: [{
      type: 'heatmap',
      coordinateSystem: 'calendar',
      data: data.value.map((d) => [d.date, d.value]),
      emphasis: { itemStyle: { borderColor: '#c8ad7e', borderWidth: 2, shadowBlur: 8, shadowColor: '#c8ad7e66' } },
    }],
  }
}

function renderChart() {
  if (!chart.value) return
  chart.value.setOption(buildOption(), true)
}

async function fetchHeatmap() {
  loading.value = true
  try {
    const res = await getHeatmapData({ year: selectedYear.value, mode: mode.value })
    data.value = res.data.data
    renderChart()
  } finally {
    loading.value = false
  }
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => chart.value?.resize())
  : null

onMounted(async () => {
  if (chartEl.value) {
    chart.value = echarts.init(chartEl.value)
    if (resizeObs) resizeObs.observe(chartEl.value)
  }
  await fetchHeatmap()
  requestAnimationFrame(() => { visible.value = true })
})

onUnmounted(() => {
  chart.value?.dispose()
  resizeObs?.disconnect()
})

watch([mode, selectedYear], fetchHeatmap)
</script>

<template>
  <div class="heat-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">热力图分析<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <div class="mode-tabs">
          <button class="tab-btn" :class="{ active: mode === 'expense' }" @click="mode = 'expense'">支出</button>
          <button class="tab-btn" :class="{ active: mode === 'income' }" @click="mode = 'income'">收入</button>
          <button class="tab-btn" :class="{ active: mode === 'net' }" @click="mode = 'net'">净额</button>
        </div>
        <div class="year-pills">
          <button v-for="y in years" :key="y" class="year-btn" :class="{ active: selectedYear === y }" @click="selectedYear = y">{{ y }}</button>
        </div>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">当前模式总额</span><span class="summary-value finance-summary-value" :class="summaryStats.total >= 0 ? 'income' : 'expense'">¥{{ Math.abs(summaryStats.total).toLocaleString('zh-CN') }}</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">活跃天数</span><span class="summary-value finance-summary-value">{{ summaryStats.activeDays }} 天</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item summary-count finance-summary-count"><span class="summary-label finance-summary-label">峰值日期</span><span class="summary-value finance-summary-value">{{ summaryStats.peak.date }}</span></div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <div class="chart-wrap" v-loading="loading">
      <div ref="chartEl" class="heatmap-chart" />
      <div v-if="!loading && data.length === 0" class="empty">暂无热力图数据</div>
    </div>
  </div>
</template>

<style scoped>
.mode-tabs, .year-pills { display: flex; gap: 6px; }
.tab-btn, .year-btn { padding: 6px 14px; border-radius: var(--radius-sm); border: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-muted); font-size: 13px; cursor: pointer; }
.tab-btn.active, .year-btn.active { border-color: var(--color-accent); color: var(--color-accent); background: var(--color-accent-subtle); }
.chart-wrap { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 18px; min-height: 320px; position: relative; }
.heatmap-chart { width: 100%; height: 260px; }
.empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
</style>
