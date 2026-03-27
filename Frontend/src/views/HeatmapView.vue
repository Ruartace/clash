<script setup lang="ts">
import { ref, onMounted, onUnmounted, shallowRef, computed, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_COLORS } from '@/assets/styles/chart-theme'

// ── Generate mock heatmap data for current year ──────────────────────────────
function generateHeatData(year: number) {
  const data: [string, number][] = []
  const start = new Date(year, 0, 1)
  const end   = new Date(year, 11, 31)
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10)
    const day = d.getDay()
    const isWeekend = day === 0 || day === 6
    const base = isWeekend ? Math.random() * 300 : Math.random() * 600 + 100
    const spike = Math.random() < 0.08 ? Math.random() * 2000 : 0
    data.push([dateStr, Math.round(base + spike)])
  }
  return data
}

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)
const years = [currentYear - 2, currentYear - 1, currentYear]

// Income heatmap: arrives mostly on 1st and 15th
function generateIncomeData(year: number) {
  const data: [string, number][] = []
  const start = new Date(year, 0, 1)
  const end   = new Date(year, 11, 31)
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10)
    const dom = d.getDate()
    const val = dom === 1  ? 18000 + Math.round(Math.random() * 2000)
              : dom === 15 ? 4500  + Math.round(Math.random() * 500)
              : Math.random() < 0.05 ? Math.round(Math.random() * 1000) : 0
    if (val > 0) data.push([dateStr, val])
  }
  return data
}

type HeatMode = 'expense' | 'income' | 'net'
const mode = ref<HeatMode>('expense')

const expenseData = computed(() => generateHeatData(selectedYear.value))
const incomeData  = computed(() => generateIncomeData(selectedYear.value))

const activeData = computed(() => {
  if (mode.value === 'income')  return incomeData.value
  if (mode.value === 'expense') return expenseData.value
  const inc = Object.fromEntries(incomeData.value)
  return expenseData.value.map(([d, e]) => [d, (inc[d] ?? 0) - e] as [string, number])
})

const maxVal = computed(() => Math.max(...activeData.value.map(d => Math.abs(d[1]))))

// ── ECharts instance ─────────────────────────────────────────────────────────
const chartEl = ref<HTMLDivElement | null>(null)
const chart   = shallowRef<echarts.ECharts>()

function buildOption(): echarts.EChartsOption {
  const isNet    = mode.value === 'net'
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: (p: any) => {
        const val  = p.value[1] as number
        const sign = val >= 0 ? '' : '-'
        const abs  = Math.abs(val)
        return `<b style="color:#bfbebf">${p.value[0]}</b><br/>
                <span style="color:${val >= 0 ? CHART_COLORS.income : CHART_COLORS.expense}">
                  ${sign}&#165;${abs.toLocaleString('zh-CN')}
                </span>`
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
      top: 80,
      left: 40,
      right: 20,
      bottom: 50,
      range: selectedYear.value,
      itemStyle: {
        color: '#171716',
        borderColor: '#252320',
        borderWidth: 2,
      },
      dayLabel:   { color: '#7a7874', fontSize: 10, nameMap: ['日','一','二','三','四','五','六'] },
      monthLabel: { color: '#bfbebf', fontSize: 11, nameMap: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'] },
      yearLabel:  { show: false },
      splitLine:  { show: true, lineStyle: { color: '#2e2b27', width: 1 } },
    },
    series: [{
      type: 'heatmap',
      coordinateSystem: 'calendar',
      data: activeData.value,
      emphasis: {
        itemStyle: { borderColor: '#c8ad7e', borderWidth: 2, shadowBlur: 8, shadowColor: '#c8ad7e66' },
      },
    }],
  }
}

function renderChart() {
  if (!chart.value) return
  chart.value.setOption(buildOption(), true)
}

const resizeObs = typeof ResizeObserver !== 'undefined'
  ? new ResizeObserver(() => chart.value?.resize())
  : null

onMounted(() => {
  if (!chartEl.value) return
  chart.value = echarts.init(chartEl.value)
  renderChart()
  if (resizeObs) resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  chart.value?.dispose()
  resizeObs?.disconnect()
})

// Re-render when mode or year changes
watch([mode, selectedYear], renderChart)

// Summary stats
const summaryStats = computed(() => {
  const totalExp   = expenseData.value.reduce((s, d) => s + d[1], 0)
  const totalInc   = incomeData.value.reduce((s, d) => s + d[1], 0)
  const activeDays = expenseData.value.filter(d => d[1] > 0).length
  const peakDay    = expenseData.value.reduce((a, b) => b[1] > a[1] ? b : a)
  return { totalExp, totalInc, activeDays, peakDay }
})
</script>

<template>
  <div class="heat-page">
    <header class="page-header">
      <h1 class="page-title">热力图分析</h1>
      <p class="page-subtitle">ECharts 5 日历热力图 — 全年收支密度可视化</p>
    </header>

    <!-- Controls -->
    <div class="controls">
      <div class="mode-tabs">
        <button
          v-for="m in ([['expense','支出热力'],['income','收入热力'],['net','净额热力']] as const)"
          :key="m[0]"
          class="tab-btn"
          :class="{ active: mode === m[0] }"
          @click="mode = m[0]"
        >
          {{ m[1] }}
        </button>
      </div>
      <div class="year-pills">
        <button
          v-for="y in years"
          :key="y"
          class="year-btn"
          :class="{ active: selectedYear === y }"
          @click="selectedYear = y"
        >
          {{ y }}
        </button>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="summary-bar">
      <div class="s-card">
        <p class="s-label">年度总支出</p>
        <p class="s-val expense">¥{{ summaryStats.totalExp.toLocaleString('zh-CN') }}</p>
      </div>
      <div class="s-card">
        <p class="s-label">年度总收入</p>
        <p class="s-val income">¥{{ summaryStats.totalInc.toLocaleString('zh-CN') }}</p>
      </div>
      <div class="s-card">
        <p class="s-label">有支出天数</p>
        <p class="s-val accent">{{ summaryStats.activeDays }} 天</p>
      </div>
      <div class="s-card">
        <p class="s-label">最高单日支出</p>
        <p class="s-val accent">¥{{ summaryStats.peakDay[1].toLocaleString('zh-CN') }}</p>
        <p class="s-date">{{ summaryStats.peakDay[0] }}</p>
      </div>
    </div>

    <!-- Chart -->
    <div class="chart-wrap">
      <div ref="chartEl" class="heatmap-chart" />
    </div>
  </div>
</template>

<style scoped>
.heat-page { display: flex; flex-direction: column; }

.page-header { margin-bottom: 20px; }
.page-title  { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }

.controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.mode-tabs, .year-pills {
  display: flex;
  gap: 6px;
}

.tab-btn, .year-btn {
  padding: 6px 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-family: var(--font-sans);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn.active, .year-btn.active {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.tab-btn:hover:not(.active), .year-btn:hover:not(.active) {
  border-color: var(--color-accent-dim);
  color: var(--color-text-primary);
}

.summary-bar {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.s-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}
.s-label { font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.s-val {
  font-size: 18px;
  font-weight: 700;
  font-family: var(--font-mono);
}
.s-val.expense { color: var(--color-expense); }
.s-val.income  { color: var(--color-income); }
.s-val.accent  { color: var(--color-accent); }
.s-date { font-size: 11px; color: var(--color-text-muted); margin-top: 4px; font-family: var(--font-mono); }

.chart-wrap {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  overflow: hidden;
}

.heatmap-chart {
  width: 100%;
  height: 260px;
}
</style>
