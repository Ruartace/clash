<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getMonthlySummary, getCategoryBreakdown, getNetWorth } from '@/api/statistics'
import { formatCurrency } from '@/utils/format'

const netWorth = ref({ net_worth: '0', total_assets: '0', total_liabilities: '0' })
const monthlySummary = ref<{ year: number; month: number; income: string; expense: string; balance: string }[]>([])
const categoryBreakdown = ref<{ category: string; amount: string }[]>([])
const loading = ref(true)

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

onMounted(async () => {
  try {
    await Promise.all([
      getNetWorth().then((r) => { netWorth.value = r.data.data }),
      getMonthlySummary().then((r) => { monthlySummary.value = r.data.data as unknown as typeof monthlySummary.value }),
      getCategoryBreakdown({ year: currentYear, month: currentMonth }).then((r) => { categoryBreakdown.value = r.data.data as unknown as typeof categoryBreakdown.value }),
    ])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="statistics-page">
    <header class="page-header">
      <h1 class="page-title">统计分析</h1>
      <p class="page-subtitle">可视化您的财务数据</p>
    </header>

    <div class="stat-grid" v-loading="loading">
      <div class="stat-card highlight">
        <p class="stat-label">净资产</p>
        <p class="stat-value">{{ formatCurrency(netWorth.net_worth) }}</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">总资产</p>
        <p class="stat-value income">{{ formatCurrency(netWorth.total_assets) }}</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">总负债</p>
        <p class="stat-value expense">{{ formatCurrency(netWorth.total_liabilities) }}</p>
      </div>
    </div>

    <div class="charts-row">
      <!-- Monthly income/expense table -->
      <section class="section">
        <h2 class="section-title">月度收支（{{ currentYear }}年）</h2>
        <el-table :data="monthlySummary" style="width:100%" size="small">
          <el-table-column label="月份" width="80">
            <template #default="{ row }">{{ row.month }}月</template>
          </el-table-column>
          <el-table-column label="收入">
            <template #default="{ row }">
              <span class="income">{{ formatCurrency(row.income) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="支出">
            <template #default="{ row }">
              <span class="expense">{{ formatCurrency(row.expense) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="净额">
            <template #default="{ row }">
              <span :class="parseFloat(row.balance) >= 0 ? 'income' : 'expense'">
                {{ formatCurrency(row.balance) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <!-- Category breakdown -->
      <section class="section">
        <h2 class="section-title">本月支出分类</h2>
        <div v-if="categoryBreakdown.length === 0 && !loading" class="empty">暂无数据</div>
        <div class="category-list">
          <div v-for="c in categoryBreakdown" :key="c.category" class="category-item">
            <div class="category-row">
              <span class="category-name">{{ c.category }}</span>
              <span class="category-amount">{{ formatCurrency(c.amount) }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.statistics-page { max-width: 1100px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
}
.stat-card.highlight {
  border-color: rgba(56, 189, 248, 0.3);
  background: linear-gradient(135deg, var(--color-bg-card), rgba(56,189,248,0.05));
}
.stat-label { font-size: 12px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.stat-value { font-size: 22px; font-weight: 700; font-family: var(--font-mono); color: var(--color-text-primary); }
.stat-value.income { color: var(--color-income); }
.stat-value.expense { color: var(--color-expense); }

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.section { margin-bottom: 0; }
.section-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 14px; }

.income { color: var(--color-income); font-family: var(--font-mono); font-weight: 600; }
.expense { color: var(--color-expense); font-family: var(--font-mono); font-weight: 600; }

.category-list { display: flex; flex-direction: column; gap: 12px; }
.category-row { display: flex; align-items: center; gap: 8px; }
.category-name { flex: 1; font-size: 13px; color: var(--color-text-primary); }
.category-amount { font-size: 13px; font-family: var(--font-mono); color: var(--color-expense); }
.empty { color: var(--color-text-muted); font-size: 14px; padding: 20px; }

@media (max-width: 768px) {
  .charts-row { grid-template-columns: 1fr; }
}
</style>
