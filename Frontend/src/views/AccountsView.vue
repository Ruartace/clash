<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAccountStore } from '@/store/useAccountStore'
import { createAccount, updateAccount } from '@/api/accounts'
import { formatCurrency } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Account } from '@/types'

const store = useAccountStore()
onMounted(() => store.fetchAccounts())

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

const form = ref<Partial<Account>>({
  name: '',
  account_type: 'checking',
  balance: '0.00',
  currency: 'CNY',
})

const accountTypes = [
  { label: '储蓄卡', value: 'savings' },
  { label: '信用卡', value: 'credit' },
  { label: '现金', value: 'cash' },
  { label: '投资账户', value: 'investment' },
  { label: '其他', value: 'other' },
]

function openCreate() {
  editingId.value = null
  form.value = { name: '', account_type: 'savings', balance: '0.00', currency: 'CNY' }
  dialogVisible.value = true
}

function openEdit(row: Account) {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name) {
    ElMessage.warning('请输入账户名称')
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updateAccount(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createAccount(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await store.fetchAccounts()
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="accounts-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">账户管理</h1>
        <p class="page-subtitle">管理您的所有资金账户</p>
      </div>
      <el-button type="primary" @click="openCreate">+ 新增账户</el-button>
    </header>

    <el-table
      :data="store.accounts"
      v-loading="store.loading"
      style="width: 100%"
      row-class-name="table-row"
    >
      <el-table-column prop="name" label="账户名称" min-width="140" />
      <el-table-column prop="account_type" label="类型" width="120" />
      <el-table-column label="余额" min-width="160">
        <template #default="{ row }">
          <span class="amount">{{ formatCurrency(row.balance, row.currency) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="currency" label="货币" width="80" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑账户' : '新增账户'"
      width="420px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="账户名称">
          <el-input v-model="form.name" placeholder="例：招商银行储蓄卡" />
        </el-form-item>
        <el-form-item label="账户类型">
          <el-select v-model="form.account_type" style="width: 100%">
            <el-option
              v-for="t in accountTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="初始余额">
          <el-input v-model="form.balance" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="货币">
          <el-select v-model="form.currency" style="width: 100%">
            <el-option label="人民币 CNY" value="CNY" />
            <el-option label="美元 USD" value="USD" />
            <el-option label="欧元 EUR" value="EUR" />
          </el-select>
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
.accounts-page { max-width: 1000px; }
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.amount { font-family: var(--font-mono); font-weight: 600; color: var(--color-accent); }
</style>
