<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getTransactions, createTransaction, deleteTransaction } from '@/api/transactions'
import { getAccounts } from '@/api/accounts'
import { formatCurrency, formatDate } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Transaction, Account } from '@/types'

const transactions = ref<Transaction[]>([])
const accounts = ref<Account[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const total = ref(0)
const page = ref(1)

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

onMounted(fetchData)

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
</script>

<template>
  <div class="tx-page">
    <header class="page-header">
      <div>
        <h1 class="page-title">收支流水</h1>
        <p class="page-subtitle">记录与管理您的每一笔收支</p>
      </div>
      <el-button type="primary" @click="openCreate">+ 新增记录</el-button>
    </header>

    <el-table :data="transactions" v-loading="loading" style="width:100%">
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
      <el-table-column label="金额" width="140">
        <template #default="{ row }">
          <span :class="['amount', row.transaction_type]">
            {{ row.transaction_type === 'expense' ? '-' : '+' }}{{ formatCurrency(row.amount) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="account_name" label="账户" width="120" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" title="新增流水" width="440px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="账户">
          <el-select v-model="form.account" style="width:100%">
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
          <el-date-picker v-model="form.transaction_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
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
.tx-page { max-width: 1100px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 24px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.amount { font-family: var(--font-mono); font-weight: 600; }
.amount.income { color: var(--color-income); }
.amount.expense { color: var(--color-expense); }
.amount.transfer { color: var(--color-accent); }
.pagination { margin-top: 20px; justify-content: flex-end; }
</style>
