<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

import { getMonthlySummary, getCategoryBreakdown, getNetWorth } from '@/api/statistics'
import { formatCurrency } from '@/utils/format'
import { CHART_THEME, CHART_COLORS } from '@/assets/styles/chart-theme'

interface MonthlyItem {
  year: number
  month: number
  income: string
  expense: string
  balance: string
}

interface CategoryItem {
  category: string
  amount: string
}

const netWorth = ref({ net_worth: '0', total_assets: '0', total_liabilities: '0' })
const monthlySummary = ref<MonthlyItem[]>([])
const categoryBreakdown = ref<CategoryItem[]>([])
const loading = ref(false)
const visible = ref(false)

const now = new Date()
const currentYear = now.getFullYear()
const currentMonth = now.getMonth() + 1

const selectedYear = ref(String(currentYear))
const selectedMonth = ref(`${currentYear}-${String(currentMonth).padStart(2, '0')}`)

const monthlyRows = computed(() => [...monthlySummary.value].sort((a, b) => a.month - b.month))

const annualIncome = computed(() => monthlyRows.value.reduce((s, m) => s + parseFloat(m.income || '0'), 0))
const annualExpense = computed(() => monthlyRows.value.reduce((s, m) => s + parseFloat(m.expense || '0'), 0))
const annualBalance = computed(() => annualIncome.value - annualExpense.value)
const categoryTotal = computed(() => categoryBreakdown.value.reduce((s, c) => s + parseFloat(c.amount || '0'), 0))

function categoryPercent(amount: string) {
  if (!categoryTotal.value) return 0
  return Math.round((parseFloat(amount || '0') / categoryTotal.value) * 100)
}

async function fetchStatistics() {
  loading.value = true
  try {
    const [yearText, monthText] = selectedMonth.value.split('-')
    const year = Number(yearText)
    const month = Number(monthText)

    const [netRes, monthlyRes, categoryRes] = await Promise.all([
      getNetWorth(),
      getMonthlySummary(Number(selectedYear.value)),
      getCategoryBreakdown({ year, month }),
    ])

    netWorth.value = netRes.data.data
    monthlySummary.value = monthlyRes.data.data as unknown as MonthlyItem[]
    categoryBreakdown.value = categoryRes.data.data as unknown as CategoryItem[]
  } finally {
    loading.value = false
  }
}

async function handleYearChange() {
  if (!selectedMonth.value.startsWith(selectedYear.value)) {
    selectedMonth.value = `${selectedYear.value}-${String(currentMonth).padStart(2, '0')}`
  }
  await fetchStatistics()
}

async function handleMonthChange() {
  const [yearText] = selectedMonth.value.split('-')
  selectedYear.value = yearText
  await fetchStatistics()
}

const trendEl = ref<HTMLDivElement | null>(null)
let trendChart: echarts.ECharts | null = null

function renderTrendChart() {
  if (!trendChart || !monthlyRows.value.length) return

  const labels = monthlyRows.value.map((m) => `${m.month}月`)
  const incomeData = monthlyRows.value.map((m) => Number(m.income || 0))
  const expenseData = monthlyRows.value.map((m) => Number(m.expense || 0))
  const balanceData = monthlyRows.value.map((m) => Number(m.balance || 0))

  trendChart.setOption({
    ...CHART_THEME,
    color: [CHART_COLORS.income, CHART_COLORS.expense, CHART_COLORS.primary],
    tooltip: {
      ...CHART_THEME.tooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: {
      ...CHART_THEME.legend,
      data: ['收入', '支出', '净额'],
      top: 0,
      right: 0,
      itemWidth: 12,
      itemHeight: 8,
    },
    grid: {
      left: 8,
      right: 8,
      top: 36,
      bottom: 6,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#2e2b27' } },
      axisTick: { show: false },
      axisLabel: { color: '#7a7874' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#7a7874' },
      splitLine: { lineStyle: { color: '#2e2b27', type: 'dashed', opacity: 0.5 } },
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        barMaxWidth: 14,
        data: incomeData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '支出',
        type: 'bar',
        barMaxWidth: 14,
        data: expenseData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '净额',
        type: 'line',
        data: balanceData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
        },
      },
    ],
  })
}

function initTrendChart() {
  if (!trendEl.value) return
  trendChart = echarts.init(trendEl.value)
  renderTrendChart()
}

function handleResize() {
  trendChart?.resize()
}

watch(monthlyRows, () => {
  renderTrendChart()
}, { deep: true })

onMounted(async () => {
  await fetchStatistics()
  initTrendChart()
  requestAnimationFrame(() => { visible.value = true })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  trendChart = null
})
</script>

<template>
  <div class="statistics-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">统计分析<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <el-date-picker v-model="selectedYear" type="year" value-format="YYYY" style="width: 120px" @change="handleYearChange" />
        <el-date-picker v-model="selectedMonth" type="month" value-format="YYYY-MM" style="width: 140px" @change="handleMonthChange" />
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">净资产</span>
        <span class="summary-value finance-summary-value">{{ formatCurrency(netWorth.net_worth) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">总资产</span>
        <span class="summary-value finance-summary-value income">{{ formatCurrency(netWorth.total_assets) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">总负债</span>
        <span class="summary-value finance-summary-value expense">{{ formatCurrency(netWorth.total_liabilities) }}</span>
      </div>
      <div class="summary-item finance-summary-item summary-count finance-summary-count">
        <span class="summary-label finance-summary-label">年度净额</span>
        <span class="summary-value finance-summary-value" :class="annualBalance >= 0 ? 'income' : 'expense'">{{ formatCurrency(String(annualBalance)) }}</span>
      </div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <section class="stats-grid" v-loading="loading">
      <article class="stats-card monthly-card">
        <div class="card-head">
          <h3 class="card-title">月度收支趋势 · {{ selectedYear }}年</h3>
          <p class="card-meta">收入 {{ formatCurrency(String(annualIncome)) }} · 支出 {{ formatCurrency(String(annualExpense)) }}</p>
        </div>
        <div v-if="monthlyRows.length" ref="trendEl" class="trend-chart"></div>
        <div v-else class="empty">暂无月度数据</div>
      </article>

      <article class="stats-card category-card">
        <div class="card-head">
          <h3 class="card-title">本月支出分类 · {{ selectedMonth }}</h3>
          <p class="card-meta">分类总支出 {{ formatCurrency(String(categoryTotal)) }}</p>
        </div>
        <div v-if="categoryBreakdown.length" class="category-list">
          <div v-for="c in categoryBreakdown" :key="c.category" class="category-item">
            <div class="category-row">
              <span class="category-name">{{ c.category }}</span>
              <span class="category-amount">{{ formatCurrency(c.amount) }}</span>
            </div>
            <div class="category-track">
              <div class="category-fill" :style="{ width: `${categoryPercent(c.amount)}%` }"></div>
            </div>
          </div>
        </div>
        <div v-else class="empty">暂无分类支出数据</div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.finance-summary-value.income { color: var(--color-income); }
.finance-summary-value.expense { color: var(--color-expense); }
.stats-grid { display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; }
.stats-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 16px; box-shadow: var(--shadow-card); }
.card-head { margin-bottom: 14px; }
.card-title { font-size: 14px; color: var(--color-text-primary); font-weight: 700; letter-spacing: .02em; }
.card-meta { margin-top: 4px; font-size: 12px; color: var(--color-text-muted); font-family: var(--font-mono); }
.trend-chart { width: 100%; height: 320px; }
.category-list { display: flex; flex-direction: column; gap: 10px; }
.category-item { border: 1px solid var(--color-border); background: var(--color-bg-secondary); border-radius: var(--radius-sm); padding: 10px; }
.category-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.category-name { color: var(--color-text-primary); font-size: 13px; }
.category-amount { font-family: var(--font-mono); font-size: 12px; color: var(--color-expense); }
.category-track { background: var(--color-bg-hover); border-radius: 999px; height: 8px; overflow: hidden; }
.category-fill { height: 100%; border-radius: 999px; transition: width .35s ease; background: linear-gradient(90deg, rgba(200,173,126,.4), var(--color-accent)); }
.income { color: var(--color-income); }
.expense { color: var(--color-expense); }
.empty { color: var(--color-text-muted); font-size: 13px; padding: 24px; text-align: center; }
@media (max-width: 960px) { .stats-grid { grid-template-columns: 1fr; } .trend-chart { height: 280px; } }
</style>
