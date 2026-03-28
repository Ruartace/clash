<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getBudgets, createBudget, deleteBudget } from '@/api/budgets'
import { formatCurrency } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Budget } from '@/types'

const budgets = ref<Budget[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const visible = ref(false)
const viewMode = ref<'visual' | 'manage'>('visual')

const currentMonth = new Date().toISOString().slice(0, 7)
const selectedMonth = ref(currentMonth)

const form = ref<Partial<Budget>>({
  category: '',
  amount: '',
  month: currentMonth,
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getBudgets(selectedMonth.value)
    budgets.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchData()
  requestAnimationFrame(() => { visible.value = true })
})

function openCreate() {
  form.value = { category: '', amount: '', month: selectedMonth.value }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.category || !form.value.amount) {
    ElMessage.warning('请填写分类和预算金额')
    return
  }
  submitting.value = true
  try {
    await createBudget(form.value)
    ElMessage.success('预算已设置')
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除该预算？', '提示', { type: 'warning' })
  await deleteBudget(id)
  ElMessage.success('已删除')
  await fetchData()
}

function usagePercent(budget: Budget): number {
  const spent = parseFloat(budget.spent || '0')
  const amount = parseFloat(budget.amount || '0')
  if (!amount) return 0
  return Math.min(100, Math.round((spent / amount) * 100))
}

function usageStatus(budget: Budget): 'success' | 'warning' | 'exception' {
  const pct = usagePercent(budget)
  if (pct >= 100) return 'exception'
  if (pct >= 80) return 'warning'
  return 'success'
}

const totalBudget = computed(() => budgets.value.reduce((s, b) => s + parseFloat(b.amount || '0'), 0))
const totalSpent = computed(() => budgets.value.reduce((s, b) => s + parseFloat(b.spent || '0'), 0))
const totalRemaining = computed(() => totalBudget.value - totalSpent.value)
const overallUsage = computed(() => {
  if (!totalBudget.value) return 0
  return Math.min(100, Math.round((totalSpent.value / totalBudget.value) * 100))
})

const visualItems = computed(() =>
  [...budgets.value].sort((a, b) => usagePercent(b) - usagePercent(a))
)
</script>

<template>
  <div class="budgets-page finance-shell" :class="{ 'is-visible': visible }">

    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">月度预算<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          value-format="YYYY-MM"
          placeholder="选择月份"
          style="width: 140px"
          @change="fetchData"
        />
        <div class="view-toggle finance-view-toggle">
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'visual' }" @click="viewMode='visual'">可视化</button>
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'manage' }" @click="viewMode='manage'">管理</button>
        </div>
        <el-button type="primary" @click="openCreate">＋ 新增预算</el-button>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">预算总额</span>
        <span class="summary-value finance-summary-value">{{ formatCurrency(String(totalBudget)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">已支出</span>
        <span class="summary-value finance-summary-value expense">{{ formatCurrency(String(totalSpent)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">剩余预算</span>
        <span class="summary-value finance-summary-value" :class="totalRemaining >= 0 ? 'income' : 'expense'">{{ formatCurrency(String(totalRemaining)) }}</span>
      </div>
      <div class="summary-item finance-summary-item summary-count finance-summary-count">
        <span class="summary-label finance-summary-label">整体使用率</span>
        <span class="summary-value finance-summary-value muted">{{ overallUsage }}%</span>
      </div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <section v-if="viewMode === 'visual'" class="visual-panel" v-loading="loading">
      <div v-if="visualItems.length" class="visual-list">
        <article v-for="item in visualItems" :key="item.id" class="visual-item">
          <div class="vi-head">
            <span class="vi-category">{{ item.category }}</span>
            <span class="vi-percent" :class="usageStatus(item)">{{ usagePercent(item) }}%</span>
          </div>
          <div class="vi-amounts">
            <span class="spent">{{ formatCurrency(item.spent) }}</span>
            <span class="sep">/</span>
            <span class="total">{{ formatCurrency(item.amount) }}</span>
          </div>
          <el-progress :percentage="usagePercent(item)" :status="usageStatus(item)" :stroke-width="8" />
        </article>
      </div>
      <div v-else class="empty">本月暂无预算，点击新增预算开始设置</div>
    </section>

    <section v-if="viewMode === 'manage'" class="budget-grid" v-loading="loading">
      <article v-for="b in budgets" :key="b.id" class="budget-card">
        <div class="budget-card-header">
          <span class="budget-category">{{ b.category }}</span>
          <el-button link type="danger" size="small" @click="handleDelete(b.id)">删除</el-button>
        </div>
        <div class="budget-amounts">
          <span class="spent">{{ formatCurrency(b.spent) }}</span>
          <span class="sep">/</span>
          <span class="total">{{ formatCurrency(b.amount) }}</span>
        </div>
        <el-progress :percentage="usagePercent(b)" :status="usageStatus(b)" :stroke-width="6" />
      </article>
      <div v-if="budgets.length === 0 && !loading" class="empty">本月暂无预算，点击新增预算开始设置</div>
    </section>

    <el-dialog v-model="dialogVisible" title="新增预算" width="min(400px, 92vw)" align-center>
      <el-form :model="form" label-width="80px" class="finance-dialog-form">
        <el-form-item label="分类">
          <el-input v-model="form.category" placeholder="例：餐饮、交通" />
        </el-form-item>
        <el-form-item label="预算金额">
          <el-input v-model="form.amount" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="月份">
          <el-date-picker v-model="form.month" type="month" value-format="YYYY-MM" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="finance-dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<style scoped>
.finance-summary-value.expense { color: var(--color-expense); }
.finance-summary-value.income { color: var(--color-income); }
.finance-summary-value.muted { color: var(--color-text-primary); }
.visual-panel { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 18px; box-shadow: var(--shadow-card); }
.visual-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.visual-item { border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 14px; background: var(--color-bg-secondary); }
.vi-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.vi-category { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.vi-percent { font-size: 12px; font-family: var(--font-mono); }
.vi-percent.success { color: var(--color-success); }
.vi-percent.warning { color: var(--color-warning); }
.vi-percent.exception { color: var(--color-danger); }
.vi-amounts { margin-bottom: 10px; font-family: var(--font-mono); }
.budget-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
.budget-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 18px 20px; box-shadow: var(--shadow-card); }
.budget-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.budget-category { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.budget-amounts { margin-bottom: 10px; font-family: var(--font-mono); }
.spent { font-size: 16px; font-weight: 700; color: var(--color-warning); }
.sep { margin: 0 4px; color: var(--color-text-muted); }
.total { font-size: 14px; color: var(--color-text-secondary); }
.empty { color: var(--color-text-muted); font-size: 14px; padding: 32px; text-align: center; }
.dialog-form { padding: 8px 0; }

</style>
