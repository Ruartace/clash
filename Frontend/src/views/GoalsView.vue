<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getGoals, createGoal, updateGoal, deleteGoal } from '@/api/goals'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Goal } from '@/types'

const goals = ref<Goal[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)

const form = ref<Partial<Goal>>({
  name: '',
  target_amount: '',
  current_amount: '0.00',
  deadline: '',
  description: '',
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getGoals()
    goals.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

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
  const cur = parseFloat(goal.current_amount)
  const target = parseFloat(goal.target_amount)
  if (!target) return 0
  return Math.min(100, Math.round((cur / target) * 100))
}
</script>

<template>
  <div class="goals-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">财务目标</h1>
        <p class="page-subtitle">设定储蓄目标，追踪进度</p>
      </div>
      <el-button type="primary" @click="openCreate">+ 新增目标</el-button>
    </header>

    <div class="goals-grid" v-loading="loading">
      <div v-for="g in goals" :key="g.id" class="goal-card" :class="{ completed: g.is_completed }">
        <div class="goal-header">
          <span class="goal-name">{{ g.name }}</span>
          <el-tag v-if="g.is_completed" type="success" size="small">已完成</el-tag>
          <el-button link type="danger" size="small" @click="handleDelete(g.id)">删除</el-button>
        </div>
        <div class="goal-amounts">
          <span class="current">{{ formatCurrency(g.current_amount) }}</span>
          <span class="sep">/</span>
          <span class="target">{{ formatCurrency(g.target_amount) }}</span>
        </div>
        <el-progress
          :percentage="progress(g)"
          :status="g.is_completed ? 'success' : undefined"
          :stroke-width="6"
          class="goal-progress"
        />
        <div class="goal-footer">
          <span class="deadline">截止：{{ formatDate(g.deadline) }}</span>
          <span class="pct">{{ progress(g) }}%</span>
        </div>
      </div>
      <div v-if="goals.length === 0 && !loading" class="empty">
        暂无财务目标，点击新增目标开始规划
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="新增目标" width="420px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="目标名称">
          <el-input v-model="form.name" placeholder="例：应急基金" />
        </el-form-item>
        <el-form-item label="目标金额">
          <el-input v-model="form.target_amount" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="当前存款">
          <el-input v-model="form.current_amount" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.deadline" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" />
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
.goals-page { max-width: 1100px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.goal-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: border-color 0.2s;
}
.goal-card.completed { border-color: rgba(52, 211, 153, 0.4); }
.goal-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.goal-name { flex: 1; font-size: 15px; font-weight: 600; color: var(--color-text-primary); }
.goal-amounts { margin-bottom: 10px; font-family: var(--font-mono); }
.current { font-size: 18px; font-weight: 700; color: var(--color-accent); }
.sep { margin: 0 4px; color: var(--color-text-muted); }
.target { font-size: 14px; color: var(--color-text-secondary); }
.goal-footer { display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: var(--color-text-muted); }
.empty { color: var(--color-text-muted); font-size: 14px; padding: 32px; text-align: center; }
</style>
