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

onMounted(fetchData)

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
  const spent = parseFloat(budget.spent)
  const amount = parseFloat(budget.amount)
  if (!amount) return 0
  return Math.min(100, Math.round((spent / amount) * 100))
}

function usageStatus(budget: Budget): 'success' | 'warning' | 'exception' {
  const pct = usagePercent(budget)
  if (pct >= 100) return 'exception'
  if (pct >= 80) return 'warning'
  return 'success'
}
</script>

<template>
  <div class="budgets-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">月度预算</h1>
        <p class="page-subtitle">设置并追踪各分类支出预算</p>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          value-format="YYYY-MM"
          placeholder="选择月份"
          style="width:140px"
          @change="fetchData"
        />
        <el-button type="primary" @click="openCreate">+ 新增预算</el-button>
      </div>
    </header>

    <div class="budget-grid" v-loading="loading">
      <div v-for="b in budgets" :key="b.id" class="budget-card">
        <div class="budget-card-header">
          <span class="budget-category">{{ b.category }}</span>
          <el-button link type="danger" size="small" @click="handleDelete(b.id)">删除</el-button>
        </div>
        <div class="budget-amounts">
          <span class="spent">{{ formatCurrency(b.spent) }}</span>
          <span class="sep">/</span>
          <span class="total">{{ formatCurrency(b.amount) }}</span>
        </div>
        <el-progress
          :percentage="usagePercent(b)"
          :status="usageStatus(b)"
          :stroke-width="6"
          class="budget-progress"
        />
      </div>
      <div v-if="budgets.length === 0 && !loading" class="empty">
        本月暂无预算，点击新增预算开始设置
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="新增预算" width="400px">
      <el-form :model="form" label-width="80px">
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.budgets-page { max-width: 1100px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.budget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.budget-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 18px 20px;
}
.budget-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.budget-category { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.budget-amounts { margin-bottom: 10px; font-family: var(--font-mono); }
.spent { font-size: 16px; font-weight: 700; color: var(--color-warning); }
.sep { margin: 0 4px; color: var(--color-text-muted); }
.total { font-size: 14px; color: var(--color-text-secondary); }
.empty { color: var(--color-text-muted); font-size: 14px; padding: 32px; text-align: center; }
</style>
