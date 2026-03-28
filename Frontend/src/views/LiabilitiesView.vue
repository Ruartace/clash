<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getLiabilities, createLiability, deleteLiability } from '@/api/liabilities'
import { formatCurrency } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Liability } from '@/types'
import PieChart from '@/components/charts/PieChart.vue'

const liabilities = ref<Liability[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const visible = ref(false)
const viewMode = ref<'table' | 'chart'>('table')

const form = ref<Partial<Liability>>({
  name: '', liability_type: 'mortgage', principal: '', interest_rate: '', monthly_payment: '', due_date: '', description: '',
})

const liabilityTypes = [
  { label: '房贷', value: 'mortgage' },
  { label: '车贷', value: 'car_loan' },
  { label: '信用卡', value: 'credit_card' },
  { label: '消费贷', value: 'consumer_loan' },
  { label: '其他', value: 'other' },
]

const liabilityTypeMap = computed(() => Object.fromEntries(liabilityTypes.map(t => [t.value, t.label])))

async function fetchData() {
  loading.value = true
  try {
    const res = await getLiabilities()
    liabilities.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchData()
  requestAnimationFrame(() => { visible.value = true })
})

function openCreate() {
  form.value = { name: '', liability_type: 'mortgage', principal: '', interest_rate: '', monthly_payment: '', due_date: '', description: '' }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.principal) {
    ElMessage.warning('请填写名称和本金')
    return
  }
  submitting.value = true
  try {
    await createLiability(form.value)
    ElMessage.success('负债已添加')
    dialogVisible.value = false
    await fetchData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除该负债记录？', '提示', { type: 'warning' })
  await deleteLiability(id)
  ElMessage.success('已删除')
  await fetchData()
}

const totalLiability = computed(() => liabilities.value.reduce((s, l) => s + parseFloat(l.principal || '0'), 0))
const totalMonthly = computed(() => liabilities.value.reduce((s, l) => s + parseFloat(l.monthly_payment || '0'), 0))
const avgRate = computed(() => liabilities.value.length ? liabilities.value.reduce((s, l) => s + parseFloat(l.interest_rate || '0'), 0) / liabilities.value.length : 0)

const typePieData = computed(() => {
  const map: Record<string, number> = {}
  liabilities.value.forEach((l) => {
    const key = liabilityTypeMap.value[l.liability_type] ?? l.liability_type
    map[key] = (map[key] ?? 0) + parseFloat(l.principal || '0')
  })
  return Object.entries(map).map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 })).sort((a, b) => b.value - a.value)
})

const topPieData = computed(() => liabilities.value
  .map((l) => ({ name: l.name, value: parseFloat(l.principal || '0') }))
  .filter((x) => x.value > 0)
  .sort((a, b) => b.value - a.value)
  .slice(0, 8))

function liabilityTypeLabel(type: string) {
  return liabilityTypeMap.value[type] ?? type
}
</script>

<template>
  <div class="liabilities-page finance-shell" :class="{ 'is-visible': visible }">
    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">负债管理<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <div class="view-toggle finance-view-toggle">
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'table' }" @click="viewMode='table'">明细</button>
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'chart' }" @click="viewMode='chart'">图表</button>
        </div>
        <el-button type="primary" @click="openCreate">＋ 新增负债</el-button>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">负债总额</span>
        <span class="summary-value finance-summary-value expense">{{ formatCurrency(String(totalLiability)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">月供合计</span>
        <span class="summary-value finance-summary-value">{{ formatCurrency(String(totalMonthly)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">平均利率</span>
        <span class="summary-value finance-summary-value muted">{{ avgRate.toFixed(2) }}%</span>
      </div>
      <div class="summary-item finance-summary-item summary-count finance-summary-count">
        <span class="summary-label finance-summary-label">负债笔数</span>
        <span class="summary-value finance-summary-value">{{ liabilities.length }}</span>
      </div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <div v-if="viewMode === 'chart'" class="chart-grid">
      <div class="chart-card">
        <div class="chart-card-header"><span class="chart-card-label">负债类型分布</span></div>
        <PieChart v-if="typePieData.length" :data="typePieData" title="负债类型" />
        <div v-else class="chart-empty">暂无负债数据</div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><span class="chart-card-label">负债 Top 8 占比</span></div>
        <PieChart v-if="topPieData.length" :data="topPieData" title="负债占比" />
        <div v-else class="chart-empty">暂无负债数据</div>
      </div>
    </div>

    <div v-if="viewMode === 'table'" class="table-view">
      <el-table :data="liabilities" v-loading="loading" style="width:100%">
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column label="类型" width="110"><template #default="{ row }">{{ liabilityTypeLabel(row.liability_type) }}</template></el-table-column>
        <el-table-column label="本金" width="170"><template #default="{ row }"><span class="amount">{{ formatCurrency(row.principal) }}</span></template></el-table-column>
        <el-table-column label="月供" width="150"><template #default="{ row }"><span class="amount-sub">{{ formatCurrency(row.monthly_payment) }}</span></template></el-table-column>
        <el-table-column label="利率" width="100"><template #default="{ row }">{{ row.interest_rate }}%</template></el-table-column>
        <el-table-column prop="due_date" label="到期日" width="130" />
        <el-table-column prop="description" label="描述" min-width="140" />
        <el-table-column label="操作" width="80" fixed="right"><template #default="{ row }"><el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="新增负债" width="min(440px, 92vw)" align-center>
      <el-form :model="form" label-width="90px" class="finance-dialog-form">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="例：招商银行房贷" /></el-form-item>
        <el-form-item label="负债类型"><el-select v-model="form.liability_type" style="width:100%"><el-option v-for="t in liabilityTypes" :key="t.value" :label="t.label" :value="t.value" /></el-select></el-form-item>
        <el-form-item label="本金"><el-input v-model="form.principal" placeholder="0.00" /></el-form-item>
        <el-form-item label="年利率(%)"><el-input v-model="form.interest_rate" placeholder="3.5" /></el-form-item>
        <el-form-item label="月供"><el-input v-model="form.monthly_payment" placeholder="0.00" /></el-form-item>
        <el-form-item label="到期日"><el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="2" /></el-form-item>
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
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.chart-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 20px; box-shadow: var(--shadow-card); }
.chart-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.chart-card-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--color-text-muted); font-family: var(--font-mono); }
.chart-empty { height: 280px; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
.table-view { width: 100%; }
.amount { font-family: var(--font-mono); font-weight: 700; color: var(--color-expense); font-size: 15px; }
.amount-sub { font-family: var(--font-mono); color: var(--color-text-secondary); font-size: 14px; }
.finance-summary-value.expense { color: var(--color-expense); }
.finance-summary-value.muted { color: var(--color-text-primary); }
@media (max-width: 920px) { .chart-grid { grid-template-columns: 1fr; } }
</style>
