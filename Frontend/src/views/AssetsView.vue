<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getAssets, createAsset, deleteAsset } from '@/api/assets'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Asset } from '@/types'
import PieChart from '@/components/charts/PieChart.vue'

const assets = ref<Asset[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const visible = ref(false)
const viewMode = ref<'table' | 'chart'>('table')

const form = ref<Partial<Asset>>({
  name: '',
  asset_type: 'real_estate',
  current_value: '',
  purchase_price: '',
  purchase_date: '',
  description: '',
})

const assetTypes = [
  { label: '房产', value: 'real_estate' },
  { label: '车辆', value: 'vehicle' },
  { label: '股票', value: 'stock' },
  { label: '基金', value: 'fund' },
  { label: '存款', value: 'deposit' },
  { label: '其他', value: 'other' },
]

const assetTypeMap = computed(() =>
  Object.fromEntries(assetTypes.map(t => [t.value, t.label]))
)

async function fetchAssets() {
  loading.value = true
  try {
    const res = await getAssets()
    assets.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchAssets()
  requestAnimationFrame(() => { visible.value = true })
})

function openCreate() {
  form.value = {
    name: '',
    asset_type: 'real_estate',
    current_value: '',
    purchase_price: '',
    purchase_date: '',
    description: '',
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.current_value) {
    ElMessage.warning('请填写名称和当前价值')
    return
  }
  submitting.value = true
  try {
    await createAsset(form.value)
    ElMessage.success('资产已添加')
    dialogVisible.value = false
    await fetchAssets()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除该资产？', '提示', { type: 'warning' })
  await deleteAsset(id)
  ElMessage.success('已删除')
  await fetchAssets()
}

const totalAssets = computed(() =>
  assets.value.reduce((sum, a) => sum + parseFloat(a.current_value || '0'), 0)
)

const totalCost = computed(() =>
  assets.value.reduce((sum, a) => sum + parseFloat(a.purchase_price || '0'), 0)
)

const floatingPnL = computed(() => totalAssets.value - totalCost.value)

const assetTypePieData = computed(() => {
  const map: Record<string, number> = {}
  assets.value.forEach((a) => {
    const key = assetTypeMap.value[a.asset_type] ?? a.asset_type
    map[key] = (map[key] ?? 0) + parseFloat(a.current_value || '0')
  })
  return Object.entries(map)
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .sort((a, b) => b.value - a.value)
})

const assetTopPieData = computed(() =>
  assets.value
    .map((a) => ({ name: a.name, value: parseFloat(a.current_value || '0') }))
    .filter((x) => x.value > 0)
    .sort((a, b) => b.value - a.value)
    .slice(0, 8)
)

function assetTypeLabel(type: string) {
  return assetTypeMap.value[type] ?? type
}
</script>

<template>
  <div class="assets-page finance-shell" :class="{ 'is-visible': visible }">

    <header class="page-header finance-page-header">
      <div class="header-left finance-header-left">
        <p class="page-eyebrow finance-page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title finance-page-title">资产管理<span class="gold-dot finance-gold-dot">.</span></h1>
      </div>
      <div class="header-actions finance-header-actions">
        <div class="view-toggle finance-view-toggle">
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">明细</button>
          <button class="toggle-btn finance-toggle-btn" :class="{ active: viewMode === 'chart' }" @click="viewMode = 'chart'">图表</button>
        </div>
        <el-button type="primary" @click="openCreate">＋ 新增资产</el-button>
      </div>
    </header>

    <section class="summary-bar finance-summary-bar" v-loading="loading">
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">资产总额</span>
        <span class="summary-value finance-summary-value">{{ formatCurrency(String(totalAssets)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">购入成本</span>
        <span class="summary-value finance-summary-value muted">{{ formatCurrency(String(totalCost)) }}</span>
      </div>
      <div class="summary-divider finance-summary-divider" />
      <div class="summary-item finance-summary-item">
        <span class="summary-label finance-summary-label">浮动盈亏</span>
        <span class="summary-value finance-summary-value" :class="floatingPnL >= 0 ? 'income' : 'expense'">
          {{ formatCurrency(String(floatingPnL)) }}
        </span>
      </div>
      <div class="summary-item finance-summary-item summary-count finance-summary-count">
        <span class="summary-label finance-summary-label">资产笔数</span>
        <span class="summary-value finance-summary-value">{{ assets.length }}</span>
      </div>
      <div class="summary-glow finance-summary-glow"></div>
    </section>

    <div v-if="viewMode === 'chart'" class="chart-view">
      <div class="chart-grid">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-label">资产类型分布</span>
          </div>
          <PieChart v-if="assetTypePieData.length" :data="assetTypePieData" title="资产类型" />
          <div v-else class="chart-empty">暂无资产数据</div>
        </div>

        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-card-label">资产 Top 8 占比</span>
          </div>
          <PieChart v-if="assetTopPieData.length" :data="assetTopPieData" title="资产占比" />
          <div v-else class="chart-empty">暂无资产数据</div>
        </div>
      </div>
    </div>

    <div v-if="viewMode === 'table'" class="table-view">
      <el-table :data="assets" v-loading="loading" style="width:100%" class="asset-table">
        <el-table-column prop="name" label="资产名称" min-width="140" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ assetTypeLabel(row.asset_type) }}</template>
        </el-table-column>
        <el-table-column label="当前价值" width="170">
          <template #default="{ row }">
            <span class="amount">{{ formatCurrency(row.current_value) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="购入价格" width="170">
          <template #default="{ row }">
            <span class="amount-sub">{{ formatCurrency(row.purchase_price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="购入日期" width="120">
          <template #default="{ row }">{{ formatDate(row.purchase_date) }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="140" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="新增资产" width="min(440px, 92vw)" align-center>
      <el-form :model="form" label-width="90px" class="finance-dialog-form">
        <el-form-item label="资产名称">
          <el-input v-model="form.name" placeholder="例：上海房产" />
        </el-form-item>
        <el-form-item label="资产类型">
          <el-select v-model="form.asset_type" style="width: 100%">
            <el-option v-for="t in assetTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="当前价值">
          <el-input v-model="form.current_value" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="购入价格">
          <el-input v-model="form.purchase_price" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="购入日期">
          <el-date-picker v-model="form.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.chart-card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 20px; box-shadow: var(--shadow-card); }
.chart-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.chart-card-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--color-text-muted); font-family: var(--font-mono); }
.chart-empty { height: 280px; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); }
.table-view { width: 100%; }
.amount { font-family: var(--font-mono); font-weight: 700; color: var(--color-accent); font-size: 15px; }
.amount-sub { font-family: var(--font-mono); color: var(--color-text-secondary); font-size: 14px; }
.finance-summary-value.muted { color: var(--color-text-primary); }
.finance-summary-value.income { color: var(--color-income); }
.finance-summary-value.expense { color: var(--color-expense); }
.dialog-form { padding: 8px 0; }

@media (max-width: 920px) { .chart-grid { grid-template-columns: 1fr; } }
</style>
