<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getLiabilities, createLiability, deleteLiability } from '@/api/liabilities'
import { formatCurrency } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Liability } from '@/types'

const liabilities = ref<Liability[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)

const form = ref<Partial<Liability>>({
  name: '',
  liability_type: 'mortgage',
  principal: '',
  interest_rate: '',
  monthly_payment: '',
  due_date: '',
  description: '',
})

const liabilityTypes = [
  { label: '房贷', value: 'mortgage' },
  { label: '车贷', value: 'car_loan' },
  { label: '信用卡', value: 'credit_card' },
  { label: '消费贷', value: 'consumer_loan' },
  { label: '其他', value: 'other' },
]

async function fetchData() {
  loading.value = true
  try {
    const res = await getLiabilities()
    liabilities.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

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
</script>

<template>
  <div class="liabilities-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">负债管理</h1>
        <p class="page-subtitle">记录贷款与负债，掌握净资产</p>
      </div>
      <el-button type="primary" @click="openCreate">+ 新增负债</el-button>
    </header>

    <el-table :data="liabilities" v-loading="loading" style="width:100%">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="liability_type" label="类型" width="100" />
      <el-table-column label="本金" width="150">
        <template #default="{ row }">
          <span class="amount">{{ formatCurrency(row.principal) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="月供" width="130">
        <template #default="{ row }">
          <span class="amount-sub">{{ formatCurrency(row.monthly_payment) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="利率" width="90">
        <template #default="{ row }">{{ row.interest_rate }}%</template>
      </el-table-column>
      <el-table-column prop="due_date" label="到期日" width="120" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增负债" width="440px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="例：招商银行房贷" />
        </el-form-item>
        <el-form-item label="负债类型">
          <el-select v-model="form.liability_type" style="width:100%">
            <el-option v-for="t in liabilityTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="本金">
          <el-input v-model="form.principal" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="年利率(%)">
          <el-input v-model="form.interest_rate" placeholder="3.5" />
        </el-form-item>
        <el-form-item label="月供">
          <el-input v-model="form.monthly_payment" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="到期日">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
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
.liabilities-page { max-width: 1100px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.amount { font-family: var(--font-mono); font-weight: 600; color: var(--color-expense); }
.amount-sub { font-family: var(--font-mono); color: var(--color-text-secondary); }
</style>
