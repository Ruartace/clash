<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { formatCurrency } from '@/utils/format'
import { getNetWorth, getMonthlySummary } from '@/api/statistics'
import { useAccountStore } from '@/store/useAccountStore'
import type { MonthlySummary } from '@/types'

const accountStore = useAccountStore()
const netWorthData = ref({ net_worth: '0', total_assets: '0', total_liabilities: '0' })
const monthlySummary = ref<MonthlySummary[]>([])
const loading = ref(true)
const visible = ref(false)

onMounted(async () => {
  try {
    await Promise.all([
      accountStore.fetchAccounts(),
      getNetWorth().then((r) => { netWorthData.value = r.data.data }),
      getMonthlySummary().then((r) => { monthlySummary.value = r.data.data }),
    ])
  } finally {
    loading.value = false
    requestAnimationFrame(() => { visible.value = true })
  }
})

const latestMonth = computed(() => {
  if (!monthlySummary.value.length) return null
  return monthlySummary.value[monthlySummary.value.length - 1]
})

const liabilityRatio = computed(() => {
  const assets = parseFloat(netWorthData.value.total_assets)
  const liabilities = parseFloat(netWorthData.value.total_liabilities)
  if (!assets || assets <= 0) return 0
  return Math.min(100, Math.round((liabilities / assets) * 100))
})

const healthScore = computed(() => Math.max(0, 100 - liabilityRatio.value))

const healthLabel = computed(() => {
  const s = healthScore.value
  if (s >= 80) return { text: '优秀', color: 'var(--color-success)' }
  if (s >= 60) return { text: '良好', color: 'var(--color-accent)' }
  if (s >= 40) return { text: '一般', color: 'var(--color-warning)' }
  return { text: '注意', color: 'var(--color-danger)' }
})

const ringDashoffset = computed(() => 251.2 - (healthScore.value / 100) * 251.2)

const typeMap: Record<string, string> = {
  checking: '活期', savings: '储蓄', credit: '信用',
  investment: '投资', cash: '现金', other: '其他',
}
const typeIconMap: Record<string, string> = {
  checking: '🏦', savings: '💰', credit: '💳',
  investment: '📈', cash: '💵', other: '🗂️',
}
function typeLabel(t: string) { return typeMap[t] ?? t }
function typeIcon(t: string) { return typeIconMap[t] ?? '🗂️' }
</script>

<template>
  <div class="dashboard" :class="{ 'is-visible': visible }">

    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <p class="page-eyebrow">CLASH · FINANCIAL OS</p>
        <h1 class="page-title">财务总览<span class="gold-dot">.</span></h1>
      </div>
      <div class="header-badge" v-if="!loading">
        <span class="badge-dot" :style="{ background: healthLabel.color }"></span>
        <span class="badge-text">财务状态</span>
        <span class="badge-status" :style="{ color: healthLabel.color }">{{ healthLabel.text }}</span>
      </div>
    </header>

    <!-- Hero Grid -->
    <div class="hero-grid" v-loading="loading">

      <!-- Net Worth -->
      <div class="hero-card card-networth">
        <div class="card-label">净资产总量</div>
        <div class="card-main-value">{{ formatCurrency(netWorthData.net_worth) }}</div>
        <div class="networth-breakdown">
          <div class="breakdown-item">
            <span class="bk-dot" style="background: var(--color-income)"></span>
            <span class="bk-label">总资产</span>
            <span class="bk-val income">{{ formatCurrency(netWorthData.total_assets) }}</span>
          </div>
          <div class="bk-sep"></div>
          <div class="breakdown-item">
            <span class="bk-dot" style="background: var(--color-expense)"></span>
            <span class="bk-label">总负债</span>
            <span class="bk-val expense">{{ formatCurrency(netWorthData.total_liabilities) }}</span>
          </div>
        </div>
        <div class="networth-glow"></div>
      </div>

      <!-- Health Score -->
      <div class="hero-card card-health">
        <div class="card-label">财务健康度</div>
        <div class="ring-wrap">
          <svg class="ring-svg" viewBox="0 0 100 100">
            <circle class="ring-track" cx="50" cy="50" r="40" />
            <circle
              class="ring-progress"
              cx="50" cy="50" r="40"
              :style="{ stroke: healthLabel.color, strokeDashoffset: ringDashoffset + 'px' }"
            />
          </svg>
          <div class="ring-inner">
            <span class="ring-score" :style="{ color: healthLabel.color }">{{ healthScore }}</span>
            <span class="ring-unit">分</span>
          </div>
        </div>
        <div class="health-footer">
          <span class="health-status" :style="{ color: healthLabel.color }">{{ healthLabel.text }}</span>
          <span class="health-ratio">负债率 {{ liabilityRatio }}%</span>
        </div>
      </div>

      <!-- Monthly Summary -->
      <div class="hero-card card-month" v-if="latestMonth">
        <div class="card-label">本月概况</div>
        <div class="month-badge">{{ latestMonth.month }}</div>
        <div class="month-rows">
          <div class="month-row-item">
            <div class="month-row-icon income-bg">↑</div>
            <div class="month-row-info">
              <span class="mri-label">收入</span>
              <span class="mri-val income">{{ formatCurrency(latestMonth.income) }}</span>
            </div>
          </div>
          <div class="month-row-item">
            <div class="month-row-icon expense-bg">↓</div>
            <div class="month-row-info">
              <span class="mri-label">支出</span>
              <span class="mri-val expense">{{ formatCurrency(latestMonth.expense) }}</span>
            </div>
          </div>
          <div class="month-net-line">
            <span class="net-label">月结余</span>
            <span class="net-val" :class="parseFloat(latestMonth.net) >= 0 ? 'income' : 'expense'">
              {{ formatCurrency(latestMonth.net) }}
            </span>
          </div>
        </div>
      </div>
      <div class="hero-card card-month" v-else-if="!loading">
        <div class="card-label">本月概况</div>
        <div class="no-data">暂无月度数据</div>
      </div>

      <!-- Account Count -->
      <div class="hero-card card-accounts">
        <div class="card-label">关联账户</div>
        <div class="acct-count">{{ accountStore.accounts.length }}</div>
        <div class="acct-sub">个账户追踪中</div>
        <div class="acct-chips">
          <span
            v-for="acc in accountStore.accounts.slice(0, 5)"
            :key="acc.id"
            class="acct-chip"
          >{{ typeIcon(acc.account_type) }}</span>
          <span v-if="accountStore.accounts.length > 5" class="acct-more">
            +{{ accountStore.accounts.length - 5 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Accounts Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">我的账户</h2>
        <span class="section-badge">{{ accountStore.accounts.length }}</span>
      </div>
      <div class="account-grid" v-loading="loading">
        <div
          v-for="(acc, i) in accountStore.accounts"
          :key="acc.id"
          class="account-card"
          :style="{ animationDelay: `${i * 55}ms` }"
        >
          <div class="acct-card-top">
            <div class="acct-card-icon">{{ typeIcon(acc.account_type) }}</div>
            <div class="acct-card-meta">
              <div class="acct-card-name">{{ acc.name }}</div>
              <div class="acct-card-type">{{ typeLabel(acc.account_type) }}</div>
            </div>
            <div class="acct-card-currency">{{ acc.currency }}</div>
          </div>
          <div class="acct-card-balance">{{ formatCurrency(acc.balance, acc.currency) }}</div>
          <div class="acct-card-bar"><div class="acct-card-bar-fill"></div></div>
        </div>
        <div v-if="accountStore.accounts.length === 0 && !loading" class="empty-accounts">
          <div class="empty-icon">🏦</div>
          <div class="empty-text">暂无账户，请先添加账户</div>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* ── Base ─────────────────────────────────────────────────────────────── */
.dashboard {
  width: 100%;
  max-width: 100%;
  padding: 0 0 24px;
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.dashboard.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── Header ───────────────────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
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
.header-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 14px;
}
.badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: pulse-dot 2.5s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.65); }
}
.badge-text { color: var(--color-text-muted); }
.badge-status { font-weight: 600; }

/* ── Hero Grid ────────────────────────────────────────────────────────── */
.hero-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1.3fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}
@media (max-width: 1080px) {
  .hero-grid { grid-template-columns: 1fr 1fr; }
  .card-networth { grid-column: 1 / -1; }
}
@media (max-width: 560px) {
  .hero-grid { grid-template-columns: 1fr; }
  .card-networth { grid-column: auto; }
}

.hero-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-card);
  position: relative;
  overflow: hidden;
  transition: border-color var(--transition-base), box-shadow var(--transition-base),
              transform var(--transition-base);
  animation: card-in 0.5s ease both;
}
.hero-card:hover {
  border-color: var(--color-border-gold);
  box-shadow: var(--shadow-gold);
  transform: translateY(-2px);
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.hero-card:nth-child(1) { animation-delay: 0.06s; }
.hero-card:nth-child(2) { animation-delay: 0.14s; }
.hero-card:nth-child(3) { animation-delay: 0.22s; }
.hero-card:nth-child(4) { animation-delay: 0.30s; }

.card-label {
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  margin-bottom: 10px;
}

/* ── Net Worth Card ───────────────────────────────────────────────────── */
.card-networth {
  background: linear-gradient(135deg, var(--color-bg-card) 0%, rgba(200,173,126,0.07) 100%);
  border-color: var(--color-border-gold);
}
.card-main-value {
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 700;
  color: var(--color-accent);
  font-family: var(--font-mono);
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 14px;
}
.networth-breakdown {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.breakdown-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.bk-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}
.bk-label { font-size: 14px; color: var(--color-text-muted); }
.bk-val {
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-mono);
}
.bk-val.income  { color: var(--color-income); }
.bk-val.expense { color: var(--color-expense); }
.bk-sep { width: 1px; height: 18px; background: var(--color-border); }
.networth-glow {
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

/* ── Health Ring Card ─────────────────────────────────────────────────── */
.card-health {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
}
.ring-wrap {
  position: relative;
  width: 106px;
  height: 106px;
  flex-shrink: 0;
}
.ring-svg {
  width: 106px;
  height: 106px;
  transform: rotate(-90deg);
}
.ring-track {
  fill: none;
  stroke: var(--color-bg-hover);
  stroke-width: 8;
}
.ring-progress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 251.2;
  transition: stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1), stroke 0.3s ease;
}
.ring-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-score {
  font-size: 28px;
  font-weight: 700;
  font-family: var(--font-mono);
  line-height: 1;
}
.ring-unit { font-size: 13px; color: var(--color-text-muted); }
.health-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.health-status { font-size: 15px; font-weight: 600; }
.health-ratio  { font-size: 13px; color: var(--color-text-muted); }

/* ── Monthly Card ─────────────────────────────────────────────────────── */
.month-badge {
  display: inline-block;
  font-size: 13px;
  font-family: var(--font-mono);
  color: var(--color-accent);
  background: var(--color-accent-subtle);
  border: 1px solid var(--color-border-gold);
  border-radius: var(--radius-sm);
  padding: 3px 10px;
  margin-bottom: 12px;
}
.month-rows { display: flex; flex-direction: column; gap: 8px; }
.month-row-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.month-row-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}
.income-bg  { background: rgba(76,175,130,0.15); color: var(--color-income); }
.expense-bg { background: rgba(224,92,92,0.15);  color: var(--color-expense); }
.month-row-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.mri-label { font-size: 13px; color: var(--color-text-muted); }
.mri-val   { font-size: 16px; font-weight: 600; font-family: var(--font-mono); }
.mri-val.income  { color: var(--color-income); }
.mri-val.expense { color: var(--color-expense); }
.month-net-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
  margin-top: 2px;
}
.net-label { font-size: 13px; color: var(--color-text-muted); }
.net-val   { font-size: 18px; font-weight: 700; font-family: var(--font-mono); }
.net-val.income  { color: var(--color-income); }
.net-val.expense { color: var(--color-expense); }
.no-data {
  font-size: 15px;
  color: var(--color-text-muted);
  margin-top: 16px;
  text-align: center;
}

/* ── Account Count Card ───────────────────────────────────────────────── */
.card-accounts {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 4px;
}
.acct-count {
  font-size: 56px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-primary);
  line-height: 1;
}
.acct-sub { font-size: 14px; color: var(--color-text-muted); margin-bottom: 10px; }
.acct-chips { display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; }
.acct-chip {
  font-size: 22px;
  line-height: 1;
  filter: drop-shadow(0 0 4px rgba(200,173,126,0.3));
}
.acct-more {
  font-size: 13px;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  align-self: center;
}

/* ── Accounts Section ─────────────────────────────────────────────────── */
.section { margin-bottom: 24px; }
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.section-badge {
  font-size: 13px;
  font-family: var(--font-mono);
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border: 1px solid var(--color-border-gold);
  border-radius: 999px;
  padding: 2px 10px;
  line-height: 1.6;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}
@media (max-width: 560px) {
  .account-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 380px) {
  .account-grid { grid-template-columns: 1fr; }
}

.account-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition-base), transform var(--transition-base);
  animation: card-in 0.45s ease both;
  cursor: default;
}
.account-card:hover {
  border-color: var(--color-border-gold);
  transform: translateY(-2px);
}
.acct-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.acct-card-icon { font-size: 24px; line-height: 1; flex-shrink: 0; }
.acct-card-meta { flex: 1; min-width: 0; }
.acct-card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.acct-card-type {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 1px;
}
.acct-card-currency {
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--color-accent-dim);
  background: var(--color-accent-subtle);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  flex-shrink: 0;
}
.acct-card-balance {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-accent);
  font-family: var(--font-mono);
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}
.acct-card-bar {
  height: 2px;
  background: var(--color-bg-hover);
  border-radius: 1px;
  overflow: hidden;
}
.acct-card-bar-fill {
  height: 100%;
  width: 60%;
  background: linear-gradient(90deg, var(--color-accent-dim), var(--color-accent));
  border-radius: 1px;
  animation: bar-fill 1.2s cubic-bezier(0.4,0,0.2,1) both;
}
@keyframes bar-fill {
  from { width: 0; }
}

.empty-accounts {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px;
  color: var(--color-text-muted);
}
.empty-icon { font-size: 40px; }
.empty-text { font-size: 16px; }
</style>
