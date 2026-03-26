<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getAssets, createAsset, deleteAsset } from '@/api/assets'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Asset } from '@/types'

const assets = ref<Asset[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)

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

async function fetchAssets() {
  loading.value = true
  try {
    const res = await getAssets()
    assets.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchAssets)

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
</script>

<template>
  <div class="assets-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">资产管理</h1>
        <p class="page-subtitle">追踪您的固定资产与金融资产</p>
      </div>
      <el-button type="primary" @click="openCreate">+ 新增资产</el-button>
    </header>

    <el-table :data="assets" v-loading="loading" style="width:100%">
      <el-table-column prop="name" label="资产名称" min-width="140" />
      <el-table-column prop="asset_type" label="类型" width="100" />
      <el-table-column label="当前价值" width="160">
        <template #default="{ row }">
          <span class="amount">{{ formatCurrency(row.current_value) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="购入价格" width="160">
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
          <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增资产" width="440px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="资产名称">
          <el-input v-model="form.name" placeholder="例：上海房产" />
        </el-form-item>
        <el-form-item label="资产类型">
          <el-select v-model="form.asset_type" style="width:100%">
            <el-option
              v-for="t in assetTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="当前价值">
          <el-input v-model="form.current_value" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="购入价格">
          <el-input v-model="form.purchase_price" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="购入日期">
          <el-date-picker
            v-model="form.purchase_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
.assets-page { max-width: 1100px; }
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.amount { font-family: var(--font-mono); font-weight: 600; color: var(--color-income); }
.amount-sub { font-family: var(--font-mono); color: var(--color-text-secondary); }
</style>
