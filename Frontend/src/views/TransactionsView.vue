<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getTransactions, createTransaction, deleteTransaction } from '@/api/transactions'
import { getAccounts } from '@/api/accounts'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Transaction, Account } from '@/types'
import PieChart from '@/components/charts/PieChart.vue'

const transactions = ref<Transaction[]>([])
const accounts = ref<Account[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const total = ref(0)
const page = ref(1)
const visible = ref(false)
const viewMode = ref<'table' | 'chart'>('table')

const form = ref<Partial<Transaction>>({
  account: undefined,
  transaction_type: 'expense',
  amount: '',
  category: '',
  description: '',
  transaction_date: new Date().toISOString().slice(0, 10),
})

async function fetchData() {
  loading.value = true
  try {
    const [txRes, accRes] = await Promise.all([
      getTransactions({ page: page.value }),
      getAccounts(),
    ])
    transactions.value = txRes.data.data
    total.value = transactions.value.length
    accounts.value = accRes.data.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchData()
  requestAnimationFrame(() => { visible.value = true })
})

function openCreate() {
  form.value = {
    account: accounts.value[0]?.id,
    transaction_type: 'expense',
    amount: '',
    category: '',
    description: '',
    transaction_date: new Date().toISOString().slice(0, 10),
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.amount || !form.value.account) {
    ElMessage.warning('请填写必要信息')
    return
  }
  submitting.value = true
  try {
    await createTransaction(form.value)
    ElMessage.success('记录成功')
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' })
  await deleteTransaction(id)
  ElMessage.success('已删除')
  await fetchData()
}

function typeLabel(t: string) {
  return { income: '收入', expense: '支出', transfer: '转账' }[t] ?? t
}
function typeTag(t: string): 'success' | 'danger' | 'info' {
  return ({ income: 'success', expense: 'danger', transfer: 'info' } as const)[t] ?? 'info'
}

const totalIncome = computed(() =>
  transactions.value
    .filter(t => t.transaction_type === 'income')
    .reduce((s, t) => s + parseFloat(t.amount || '0'), 0)
)
const totalExpense = computed(() =>
  transactions.value
    .filter(t => t.transaction_type === 'expense')
    .reduce((s, t) => s + parseFloat(t.amount || '0'), 0)
)
const netAmount = computed(() => totalIncome.value - totalExpense.value)

const expensePieData = computed(() => {
  const map: Record<string, number> = {}
  transactions.value
    .filter(t => t.transaction_type === 'expense')
    .forEach(t => {
      const cat = t.category || '其他'
      map[cat] = (map[cat] ?? 0) + parseFloat(t.amount || '0')
    })
  return Object.entries(map)
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .sort((a, b) => b.value - a.value)
})

const incomePieData = computed(() => {
  const map: Record<string, number> = {}
  transactions.value
    .filter(t => t.transaction_type === 'income')
    .forEach(t => {
      const cat = t.category || '其他'
      map[cat] = (map[cat] ?? 0) + parseFloat(t.amount || '0')
    })
  return Object.entries(map)
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .sort((a, b) => b.value - a.value)
})
</script>

<template>
  <div class="tx-page" :class="{ 'is-visible': visible }">

    <!-- Page Header -->
    <header class="page-header">
      <div class="header-left">
        <p class="page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title">收支流水<span class="gold-dot">.</span></h1>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <button class="toggle-btn" :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">明细</button>
          <button class="toggle-btn" :class="{ active: viewMode === 'chart' }" @click="viewMode = 'chart'">图表</button>
        </div>
        <el-button type="primary" @click="openCreate">＋ 新增记录</el-button>
      </div>
    </header>

    <!-- Summary Bar -->
    <section class="summary-bar" v-loading="loading">
      <div class="summary-item">
        <span class="summary-label">收入</span>
        <span class="summary-value income">{{ formatCurrency(String(totalIncome)) }}</span>
      </div>
      <div class="summary-divider" />
      <div class="summary-item">
        <span class="summary-label">支出</span>
        <span class="summary-value expense">{{ formatCurrency(String(totalExpense)) }}</span>
      </div>
      <div class="summary-divider" />
      <div class="summary-item">
        <span class="summary-label">净收支</span>
        <span class="summary-value" :class="netAmount >= 0 ? 'income' : 'expense'">
          {{ formatCurrency(String(netAmount)) }}
        </span>
      </div>
      <div class="summary-item">
        <span class="summary-label">笔数</span>
        <span class="summary-value">{{ transactions.length }}</span>
      </div>
      <div class="summary-glow"></div>
    </section>

    <!-- Chart View -->
    <div v-if="viewMode === 'chart'" class="chart-view">
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-label">支出分类分布</span>
            <span class="chart-card-total expense">{{ formatCurrency(String(totalExpense)) }}</span>
          </div>
          <PieChart v-if="expensePieData.length" :data="expensePieData" title="支出分类" />
          <div v-else class="chart-empty">暂无支出数据</div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-label">收入分类分布</span>
            <span class="chart-card-total income">{{ formatCurrency(String(totalIncome)) }}</span>
          </div>
          <PieChart v-if="incomePieData.length" :data="incomePieData" title="收入分类" />
          <div v-else class="chart-empty">暂无收入数据</div>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-if="viewMode === 'table'" class="table-view">
      <el-table :data="transactions" v-loading="loading" style="width: 100%" class="tx-table">
        <el-table-column prop="transaction_date" label="日期" width="110">
          <template #default="{ row }">{{ formatDate(row.transaction_date) }}</template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.transaction_type)" size="small">
              {{ typeLabel(row.transaction_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="description" label="描述" min-width="160" />
        <el-table-column label="金额" width="150">
          <template #default="{ row }">
            <span :class="['amount', row.transaction_type]">
              {{ row.transaction_type === 'expense' ? '−' : '+' }}{{ formatCurrency(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="account_name" label="账户" width="120" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :total="total"
        :page-size="20"
        layout="prev, pager, next, total"
        class="pagination"
        @current-change="fetchData"
      />
    </div>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" title="新增流水" width="min(440px, 92vw)" align-center>
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-form-item label="账户">
          <el-select v-model="form.account" style="width: 100%">
            <el-option v-for="a in accounts" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.transaction_type">
            <el-radio value="income">收入</el-radio>
            <el-radio value="expense">支出</el-radio>
            <el-radio value="transfer">转账</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="金额">
          <el-input v-model="form.amount" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="form.category" placeholder="如：餐饮、交通" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="备注（可选）" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.transaction_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<style scoped>
/* ── Base ─────────────────────────────────────────────────────────────── */
.tx-page {
  width: 100%;
  max-width: 100%;
  padding: 0 0 24px;
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.tx-page.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── Header ───────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
.header-left { display: flex; flex-direction: column; }
.page-eyebrow {
  font-size: 12px;
  letter-spacing: 0.18em;
  color: var(--color-accent-dim);
  font-family: var(--font-mono);
  margin-bottom: 4px;
  text-transform: uppercase;
}
.page-title {
  font-size: clamp(28px, 3vw, 38px);
    font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.15;
}
.gold-dot {
  color: var(--color-accent);
  font-size: 1.3em;
  line-height: 0;
  vertical-align: -2px;
  margin-left: 2px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.view-toggle {
  display: flex;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.toggle-btn {
  padding: 7px 18px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color var(--transition-base), background var(--transition-base);
  font-family: var(--font-sans);
}
.toggle-btn.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent);
}
.toggle-btn:hover:not(.active) {
  color: var(--color-text-primary);
  background: var(--color-bg-hover);
}
.summary-bar {
  position: relative;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 20px 28px;
  background: linear-gradient(135deg, var(--color-bg-card) 0%, rgba(200,173,126,0.07) 100%);
  border: 1px solid var(--color-border-gold);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  flex-wrap: wrap;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}
.summary-item { display: flex; flex-direction: column; gap: 6px; }
.summary-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.summary-value {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}
.summary-value.income  { color: var(--color-income); }
.summary-value.expense { color: var(--color-expense); }
.summary-divider { width: 1px; height: 36px; background: var(--color-border); flex-shrink: 0; }
.summary-glow {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
  animation: shimmer-line 3.5s ease-in-out infinite;
}
@keyframes shimmer-line {
  0%, 100% { opacity: 0.2; transform: scaleX(0.5); }
  50%       { opacity: 0.6; transform: scaleX(1); }
}
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 8px;
}
.chart-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition-base);
}
.chart-card:hover { border-color: var(--color-border-gold); }
.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.chart-card-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.chart-card-total { font-size: 18px; font-weight: 700; font-family: var(--font-mono); }
.chart-card-total.income  { color: var(--color-income); }
.chart-card-total.expense { color: var(--color-expense); }
.chart-empty {
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--color-text-muted);
}
.table-view { width: 100%; }
.amount { font-family: var(--font-mono); font-weight: 600; font-size: 14px; }
.amount.income   { color: var(--color-income); }
.amount.expense  { color: var(--color-expense); }
.amount.transfer { color: var(--color-accent); }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.dialog-form { padding: 8px 0; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 10px; }
@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
  .summary-bar { gap: 16px; padding: 16px 18px; }
  .summary-value { font-size: 20px; }
}
@media (max-width: 480px) {
  .summary-bar { flex-direction: column; align-items: flex-start; }
  .summary-divider { width: 100%; height: 1px; }
  .view-toggle { width: 100%; }
  .toggle-btn { flex: 1; text-align: center; }
}
</style>
