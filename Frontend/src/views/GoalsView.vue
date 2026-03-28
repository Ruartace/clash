<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getGoals, createGoal, deleteGoal } from '@/api/goals'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Goal } from '@/types'

const goals = ref<Goal[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const visible = ref(false)
const viewMode = ref<'visual' | 'manage'>('visual')

const form = ref<Partial<Goal>>({ name: '', target_amount: '', current_amount: '0.00', deadline: '', description: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getGoals()
    goals.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchData()
  requestAnimationFrame(() => { visible.value = true })
})

function openCreate() {
  form.value = { name: '', target_amount: '', current_amount: '0.00', deadline: '', description: '' }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.target_amount) {
    ElMessage.warning('请填写目标名称和目标金额')
    return
  }
  submitting.value = true
  try {
    await createGoal(form.value)
    ElMessage.success('目标已创建')
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除该目标？', '提示', { type: 'warning' })
  await deleteGoal(id)
  ElMessage.success('已删除')
  await fetchData()
}

function progress(goal: Goal): number {
  const cur = parseFloat(goal.current_amount || '0')
  const target = parseFloat(goal.target_amount || '0')
  if (!target) return 0
  return Math.min(100, Math.round((cur / target) * 100))
}

const totalTarget = computed(() => goals.value.reduce((s, g) => s + parseFloat(g.target_amount || '0'), 0))
const totalCurrent = computed(() => goals.value.reduce((s, g) => s + parseFloat(g.current_amount || '0'), 0))
const totalRemaining = computed(() => totalTarget.value - totalCurrent.value)
const completedCount = computed(() => goals.value.filter((g) => g.is_completed).length)
const overallProgress = computed(() => totalTarget.value ? Math.min(100, Math.round((totalCurrent.value / totalTarget.value) * 100)) : 0)
const activeGoals = computed(() => goals.value.filter((g) => !g.is_completed).sort((a, b) => progress(b) - progress(a)))
const completedGoals = computed(() => goals.value.filter((g) => g.is_completed).sort((a, b) => progress(b) - progress(a)))
</script>

<template>
  <div class="goals-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">财务目标<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <div class="view-toggle finance-view-toggle">
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'visual' }" @click="viewMode='visual'">可视化</button>
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'manage' }" @click="viewMode='manage'">管理</button>
        </div>
        <el-button type="primary" @click="openCreate">＋ 新增目标</el-button>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">目标总额</span><span class="summary-value finance-summary-value">{{ formatCurrency(String(totalTarget)) }}</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">已累计</span><span class="summary-value finance-summary-value income">{{ formatCurrency(String(totalCurrent)) }}</span></div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item"><span class="summary-label finance-summary-label">待完成</span><span class="summary-value finance-summary-value" :class="totalRemaining <= 0 ? 'income' : 'expense'">{{ formatCurrency(String(totalRemaining)) }}</span></div>
      <div class="summary-item finance-summary-item summary-count finance-summary-count"><span class="summary-label finance-summary-label">完成率 / 已完成</span><span class="summary-value finance-summary-value muted">{{ overallProgress }}% · {{ completedCount }}/{{ goals.length }}</span></div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <section v-if="viewMode === 'visual'" class="visual-panel" v-loading="loading">
      <div v-if="goals.length" class="visual-columns">
        <div class="visual-column">
          <h3 class="column-title">进行中目标</h3>
          <article v-for="g in activeGoals" :key="g.id" class="visual-item">
            <div class="vi-head"><span class="vi-name">{{ g.name }}</span><span class="vi-pct">{{ progress(g) }}%</span></div>
            <div class="vi-amounts"><span class="current">{{ formatCurrency(g.current_amount) }}</span><span class="sep">/</span><span class="target">{{ formatCurrency(g.target_amount) }}</span></div>
            <el-progress :percentage="progress(g)" :stroke-width="8" />
            <div class="vi-foot">截止：{{ g.deadline ? formatDate(g.deadline) : '未设置' }}</div>
          </article>
          <div v-if="activeGoals.length === 0" class="empty-column">暂无进行中目标</div>
        </div>

        <div class="visual-column">
          <h3 class="column-title">已完成目标</h3>
          <article v-for="g in completedGoals" :key="g.id" class="visual-item done">
            <div class="vi-head"><span class="vi-name">{{ g.name }}</span><span class="vi-pct success">100%</span></div>
            <div class="vi-amounts"><span class="current">{{ formatCurrency(g.current_amount) }}</span><span class="sep">/</span><span class="target">{{ formatCurrency(g.target_amount) }}</span></div>
            <el-progress :percentage="100" status="success" :stroke-width="8" />
            <div class="vi-foot">已达成</div>
          </article>
          <div v-if="completedGoals.length === 0" class="empty-column">暂无已完成目标</div>
        </div>
      </div>
      <div v-else class="empty">暂无财务目标，点击新增目标开始规划</div>
    </section>

    <section v-if="viewMode === 'manage'" class="goals-grid" v-loading="loading">
      <article v-for="g in goals" :key="g.id" class="goal-card" :class="{ completed: g.is_completed }">
        <div class="goal-header">
          <span class="goal-name">{{ g.name }}</span>
          <el-tag v-if="g.is_completed" type="success" size="small">已完成</el-tag>
          <el-button link type="danger" size="small" @click="handleDelete(g.id)">删除</el-button>
        </div>
        <div class="goal-amounts"><span class="current">{{ formatCurrency(g.current_amount) }}</span><span class="sep">/</span><span class="target">{{ formatCurrency(g.target_amount) }}</span></div>
        <el-progress :percentage="progress(g)" :status="g.is_completed ? 'success' : undefined" :stroke-width="6" />
        <div class="goal-footer"><span class="deadline">截止：{{ g.deadline ? formatDate(g.deadline) : '未设置' }}</span><span class="pct">{{ progress(g) }}%</span></div>
      </article>
      <div v-if="goals.length === 0 && !loading" class="empty">暂无财务目标，点击新增目标开始规划</div>
    </section>

    <el-dialog v-model="dialogVisible" title="新增目标" width="min(420px, 92vw)" align-center>
      <el-form :model="form" label-width="90px" class="finance-dialog-form">
        <el-form-item label="目标名称"><el-input v-model="form.name" placeholder="例：应急基金" /></el-form-item>
        <el-form-item label="目标金额"><el-input v-model="form.target_amount" placeholder="0.00" /></el-form-item>
        <el-form-item label="当前存款"><el-input v-model="form.current_amount" placeholder="0.00" /></el-form-item>
        <el-form-item label="截止日期"><el-date-picker v-model="form.deadline" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <div class="finance-dialog-footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button></div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.finance-summary-value.expense { color: var(--color-expense); }
.finance-summary-value.income { color: var(--color-income); }
.finance-summary-value.muted { color: var(--color-text-primary); }
.visual-panel { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 16px; box-shadow: var(--shadow-card); }
.visual-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.visual-column { border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 12px; background: var(--color-bg-secondary); }
.column-title { font-size: 13px; color: var(--color-text-muted); margin-bottom: 10px; text-transform: uppercase; letter-spacing: .08em; font-family: var(--font-mono); }
.visual-item { border: 1px solid var(--color-border); border-radius: var(--radius-sm); padding: 10px; margin-bottom: 10px; background: var(--color-bg-card); }
.visual-item.done { border-color: rgba(76, 175, 130, .35); }
.vi-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.vi-name { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.vi-pct { font-size: 12px; font-family: var(--font-mono); color: var(--color-accent); }
.vi-pct.success { color: var(--color-success); }
.vi-amounts, .goal-amounts { margin-bottom: 8px; font-family: var(--font-mono); }
.current { font-size: 16px; font-weight: 700; color: var(--color-accent); }
.sep { margin: 0 4px; color: var(--color-text-muted); }
.target { font-size: 14px; color: var(--color-text-secondary); }
.vi-foot, .goal-footer, .empty-column { font-size: 12px; color: var(--color-text-muted); }
.goals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.goal-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 18px; box-shadow: var(--shadow-card); }
.goal-card.completed { border-color: rgba(76, 175, 130, .4); }
.goal-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.goal-name { flex: 1; font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.goal-footer { display: flex; justify-content: space-between; margin-top: 8px; }
.empty { color: var(--color-text-muted); font-size: 14px; padding: 32px; text-align: center; }
.dialog-form { padding: 8px 0; }

@media (max-width: 920px) { .visual-columns { grid-template-columns: 1fr; } }
</style>
