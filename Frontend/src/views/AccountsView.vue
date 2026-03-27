<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useAccountStore } from '@/store/useAccountStore'
import { createAccount, updateAccount } from '@/api/accounts'
import { formatCurrency } from '@/utils/format'
import { ElMessage } from 'element-plus'
import type { Account } from '@/types'

const store = useAccountStore()
onMounted(() => store.fetchAccounts())

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

const form = ref<Partial<Account>>({
  name: '',
  account_type: 'debit_card',
  balance: '0.00',
  currency: 'CNY',
})

const accountTypes = [
  { label: '现金',     value: 'cash' },
  { label: '储蓄卡',   value: 'debit_card' },
  { label: '信用卡',   value: 'credit_card' },
  { label: '支付宝',   value: 'alipay' },
  { label: '微信钱包', value: 'wechat' },
  { label: '投资账户', value: 'investment' },
  { label: '其他',     value: 'other' },
]

const accountTypeMap = computed(() =>
  Object.fromEntries(accountTypes.map(t => [t.value, t.label]))
)

// Icon map per account type
const accountTypeIcon: Record<string, string> = {
  cash:        '💵',
  debit_card:  '🏦',
  credit_card: '💳',
  alipay:      '🔵',
  wechat:      '🟢',
  investment:  '📈',
  other:       '🗂️',
}

// Summary stats
const totalBalance = computed(() =>
  store.accounts.reduce((sum, a) => sum + parseFloat(a.balance || '0'), 0)
)
const accountCount = computed(() => store.accounts.length)

function openCreate() {
  editingId.value = null
  form.value = { name: '', account_type: 'debit_card', balance: '0.00', currency: 'CNY' }
  dialogVisible.value = true
}

function openEdit(row: Account) {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name?.trim()) {
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
    <!-- ── Page Header ── -->
    <header class="page-header">
      <div class="header-text">
        <h1 class="page-title">账户管理</h1>
        <p class="page-subtitle">管理您的所有资金账户</p>
      </div>
      <el-button type="primary" class="btn-add" @click="openCreate">
        <span class="btn-icon">＋</span> 新增账户
      </el-button>
    </header>

    <!-- ── Summary Bar ── -->
    <section class="summary-bar" v-loading="store.loading">
      <div class="summary-item">
        <span class="summary-label">账户总数</span>
        <span class="summary-value">{{ accountCount }}</span>
      </div>
      <div class="summary-divider" />
      <div class="summary-item">
        <span class="summary-label">资产合计（CNY）</span>
        <span class="summary-value accent">
          {{ formatCurrency(String(totalBalance), 'CNY') }}
        </span>
      </div>
    </section>

    <!-- ── Card Grid (responsive) ── -->
    <div v-if="!store.loading && store.accounts.length > 0" class="card-grid">
      <div
        v-for="account in store.accounts"
        :key="account.id"
        class="account-card"
        @click="openEdit(account)"
      >
        <div class="card-top">
          <span class="type-icon">{{ accountTypeIcon[account.account_type] ?? '🗂️' }}</span>
          <span class="type-badge">{{ accountTypeMap[account.account_type] ?? account.account_type }}</span>
        </div>
        <div class="card-name">{{ account.name }}</div>
        <div class="card-balance">{{ formatCurrency(account.balance, account.currency) }}</div>
        <div class="card-footer">
          <span class="card-currency">{{ account.currency }}</span>
          <span class="card-edit-hint">点击编辑 →</span>
        </div>
      </div>

      <!-- Add new card placeholder -->
      <div class="account-card card-add" @click="openCreate">
        <span class="add-icon">＋</span>
        <span class="add-label">新增账户</span>
      </div>
    </div>

    <!-- ── Empty State ── -->
    <div v-else-if="!store.loading" class="empty-state">
      <div class="empty-icon">🏦</div>
      <p class="empty-text">还没有账户，点击新增开始记账</p>
      <el-button type="primary" @click="openCreate">+ 新增账户</el-button>
    </div>

    <!-- ── Skeleton while loading ── -->
    <div v-if="store.loading" class="card-grid">
      <div v-for="n in 4" :key="n" class="account-card skeleton">
        <div class="sk-line sk-short" />
        <div class="sk-line sk-long" />
        <div class="sk-line sk-medium" />
      </div>
    </div>

    <!-- ── Dialog ── -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑账户' : '新增账户'"
      class="account-dialog"
      width="min(480px, 92vw)"
      align-center
    >
      <el-form :model="form" label-width="88px" class="dialog-form">
        <el-form-item label="账户名称">
          <el-input v-model="form.name" placeholder="例：招商银行储蓄卡" clearable />
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
          <el-input v-model="form.balance" placeholder="0.00">
            <template #prefix>¥</template>
          </el-input>
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
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* ── Page Shell ── */
.accounts-page {
  width: 100%;
  max-width: 1100px;
  padding: 0 4px;
  box-sizing: border-box;
}

/* ── Header ── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}
.page-title {
  font-size: clamp(20px, 3vw, 26px);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
}
.page-subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 4px;
}
.btn-add {
  white-space: nowrap;
  flex-shrink: 0;
}
.btn-icon {
  font-size: 16px;
  margin-right: 4px;
  font-style: normal;
}

/* ── Summary Bar ── */
.summary-bar {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 16px 24px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.summary-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
}
.summary-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-primary);
}
.summary-value.accent {
  color: var(--color-accent);
}
.summary-divider {
  width: 1px;
  height: 36px;
  background: var(--color-border);
  flex-shrink: 0;
}

/* ── Card Grid ── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

/* ── Account Card ── */
.account-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
  box-shadow: var(--shadow-card);
}
.account-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-gold);
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.type-icon {
  font-size: 22px;
  line-height: 1;
}
.type-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border: 1px solid var(--color-border-gold);
  white-space: nowrap;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-balance {
  font-family: var(--font-mono);
  font-size: 22px;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: -0.5px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}
.card-currency {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.card-edit-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.account-card:hover .card-edit-hint {
  opacity: 1;
  color: var(--color-accent-dim);
}

/* ── Add Card Placeholder ── */
.card-add {
  border-style: dashed;
  border-color: var(--color-border);
  background: transparent;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 140px;
}
.card-add:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
  box-shadow: none;
  transform: none;
}
.add-icon {
  font-size: 28px;
  color: var(--color-text-muted);
  line-height: 1;
  transition: color var(--transition-fast);
}
.add-label {
  font-size: 13px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}
.card-add:hover .add-icon,
.card-add:hover .add-label {
  color: var(--color-accent);
}

/* ── Skeleton ── */
.skeleton {
  cursor: default;
  pointer-events: none;
  animation: pulse 1.6s ease-in-out infinite;
}
.sk-line {
  height: 14px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-hover);
}
.sk-short  { width: 40%; }
.sk-long   { width: 80%; height: 22px; }
.sk-medium { width: 60%; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

/* ── Empty State ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 72px 24px;
  color: var(--color-text-muted);
}
.empty-icon { font-size: 48px; line-height: 1; }
.empty-text { font-size: 14px; }

/* ── Dialog ── */
.dialog-form {
  padding: 8px 0;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* ── Responsive overrides ── */
@media (max-width: 480px) {
  .summary-bar {
    gap: 16px;
    padding: 14px 16px;
  }
  .summary-value {
    font-size: 18px;
  }
  .card-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .card-balance {
    font-size: 18px;
  }
}
@media (max-width: 340px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
