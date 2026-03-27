<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useAccountStore } from '@/store/useAccountStore'
import { createAccount, updateAccount } from '@/api/accounts'
import { formatCurrency } from '@/utils/format'
import { ElMessage } from 'element-plus'
import type { Account } from '@/types'

const store = useAccountStore()
const visible = ref(false)

onMounted(async () => {
  await store.fetchAccounts()
  requestAnimationFrame(() => { visible.value = true })
})

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

const accountTypeIcon: Record<string, string> = {
  cash:        '💵',
  debit_card:  '🏦',
  credit_card: '💳',
  alipay:      '🔵',
  wechat:      '🟢',
  investment:  '📈',
  other:       '🗂️',
}

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
  <div class="accounts-page" :class="{ 'is-visible': visible }">

    <!-- ── Page Header ── -->
    <header class="page-header">
      <div class="header-left">
        <p class="page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title">账户管理<span class="gold-dot">.</span></h1>
      </div>
      <el-button type="primary" class="btn-add" @click="openCreate">
        ＋ 新增账户
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
        <span class="summary-value accent">{{ formatCurrency(String(totalBalance), 'CNY') }}</span>
      </div>
      <div class="summary-glow"></div>
    </section>

    <!-- ── Card Grid ── -->
    <div v-if="!store.loading && store.accounts.length > 0" class="card-grid">
      <div
        v-for="(account, i) in store.accounts"
        :key="account.id"
        class="account-card"
        :style="{ animationDelay: `${i * 60}ms` }"
        @click="openEdit(account)"
      >
        <div class="card-top">
          <div class="card-icon-wrap">
            <span class="type-icon">{{ accountTypeIcon[account.account_type] ?? '🗂️' }}</span>
          </div>
          <span class="type-badge">{{ accountTypeMap[account.account_type] ?? account.account_type }}</span>
        </div>
        <div class="card-name">{{ account.name }}</div>
        <div class="card-balance">{{ formatCurrency(account.balance, account.currency) }}</div>
        <div class="card-footer">
          <span class="card-currency">{{ account.currency }}</span>
          <span class="card-edit-hint">点击编辑 →</span>
        </div>
        <div class="card-bar"><div class="card-bar-fill"></div></div>
      </div>

      <!-- Add placeholder -->
      <div class="account-card card-add" @click="openCreate">
        <span class="add-icon">＋</span>
        <span class="add-label">新增账户</span>
      </div>
    </div>

    <!-- ── Skeleton ── -->
    <div v-if="store.loading" class="card-grid">
      <div v-for="n in 4" :key="n" class="account-card skeleton">
        <div class="sk-line sk-short" />
        <div class="sk-line sk-long" />
        <div class="sk-line sk-medium" />
      </div>
    </div>

    <!-- ── Empty State ── -->
    <div v-if="!store.loading && store.accounts.length === 0" class="empty-state">
      <div class="empty-icon">🏦</div>
      <p class="empty-text">还没有账户，点击新增开始记账</p>
      <el-button type="primary" @click="openCreate">＋ 新增账户</el-button>
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
            <el-option v-for="t in accountTypes" :key="t.value" :label="t.label" :value="t.value" />
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
/* ── Base ─────────────────────────────────────────────────────────────── */
.accounts-page {
  width: 100%;
  max-width: 100%;
  padding: 0 0 24px;
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.accounts-page.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── Header ───────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
.header-left {
  display: flex;
  flex-direction: column;
}
.page-eyebrow {
  font-size: 12px;
  letter-spacing: 0.18em;
  color: var(--color-accent-dim);
  font-family: var(--font-mono);
  margin-bottom: 4px;
  text-transform: uppercase;
}
.page-title {
  font-size: clamp(28px, 3vw, 38px);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.15;
}
.gold-dot {
  color: var(--color-accent);
  font-size: 1.3em;
  line-height: 0;
  vertical-align: -2px;
  margin-left: 2px;
}
.btn-add {
  white-space: nowrap;
  flex-shrink: 0;
  align-self: flex-end;
}

/* ── Summary Bar ── */
.summary-bar {
  position: relative;
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 20px 28px;
  background: linear-gradient(135deg, var(--color-bg-card) 0%, rgba(200,173,126,0.07) 100%);
  border: 1px solid var(--color-border-gold);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  flex-wrap: wrap;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.summary-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.summary-value {
  font-size: 32px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}
.summary-value.accent {
  color: var(--color-accent);
}
.summary-divider {
  width: 1px;
  height: 40px;
  background: var(--color-border);
  flex-shrink: 0;
}
.summary-glow {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
  animation: shimmer-line 3.5s ease-in-out infinite;
}
@keyframes shimmer-line {
  0%, 100% { opacity: 0.2; transform: scaleX(0.5); }
  50%       { opacity: 0.6; transform: scaleX(1); }
}

/* ── Card Grid ────────────────────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

/* ── Account Card ─────────────────────────────────────────────────────── */
.account-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
  box-shadow: var(--shadow-card);
  animation: card-in 0.5s ease both;
}
.account-card:hover {
  border-color: var(--color-border-gold);
  box-shadow: var(--shadow-gold);
  transform: translateY(-2px);
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-accent-subtle);
  border: 1px solid var(--color-border-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.type-icon {
  font-size: 20px;
  line-height: 1;
}
.type-badge {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border: 1px solid var(--color-border-gold);
  font-family: var(--font-mono);
  white-space: nowrap;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-balance {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: -0.02em;
  line-height: 1;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}
.card-currency {
  font-size: 12px;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  background: var(--color-bg-hover);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
.card-edit-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.account-card:hover .card-edit-hint {
  opacity: 1;
  color: var(--color-accent-dim);
}

.card-bar {
  height: 2px;
  background: var(--color-bg-hover);
  border-radius: 1px;
  overflow: hidden;
  margin-top: -4px;
}
.card-bar-fill {
  height: 100%;
  width: 65%;
  background: linear-gradient(90deg, var(--color-accent-dim), var(--color-accent));
  border-radius: 1px;
  animation: bar-fill 1.2s cubic-bezier(0.4,0,0.2,1) both;
}
@keyframes bar-fill {
  from { width: 0; }
}

/* ── Add Card Placeholder ── */
.card-add {
  border-style: dashed;
  border-color: var(--color-border);
  background: transparent;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 160px;
  animation: none;
}
.card-add:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
  box-shadow: none;
  transform: none;
}
.add-icon {
  font-size: 32px;
  color: var(--color-text-muted);
  line-height: 1;
  transition: color var(--transition-fast);
}
.add-label {
  font-size: 14px;
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
  padding: 80px 24px;
  color: var(--color-text-muted);
}
.empty-icon { font-size: 48px; line-height: 1; }
.empty-text { font-size: 16px; }

/* ── Dialog ── */
.dialog-form {
  padding: 8px 0;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 鈹€鈹€ Responsive 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€ */
@media (max-width: 1080px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
@media (max-width: 640px) {
  .summary-bar {
    gap: 16px;
    padding: 16px 18px;
  }
  .summary-value {
    font-size: 24px;
  }
  .card-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .card-balance {
    font-size: 20px;
  }
  .page-title {
    font-size: clamp(24px, 5vw, 32px);
  }
}
@media (max-width: 420px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
  .summary-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .summary-divider {
    width: 100%;
    height: 1px;
  }
}
</style>
