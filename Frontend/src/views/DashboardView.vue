<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { formatCurrency } from '@/utils/format'
import { getNetWorth } from '@/api/statistics'
import { getMonthlySummary } from '@/api/statistics'
import { useAccountStore } from '@/store/useAccountStore'

const accountStore = useAccountStore()

const netWorthData = ref({ net_worth: '0', total_assets: '0', total_liabilities: '0' })
const monthlySummary = ref<{ month: string; income: string; expense: string; net: string }[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    await Promise.all([
      accountStore.fetchAccounts(),
      getNetWorth().then((r) => { netWorthData.value = r.data.data }),
      getMonthlySummary().then((r) => { monthlySummary.value = r.data.data }),
    ])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard">
    <header class="page-header">
      <h1 class="page-title">财务总览</h1>
      <p class="page-subtitle">实时掌握您的财务状况</p>
    </header>

    <!-- Net worth cards -->
    <div class="stat-grid" v-loading="loading">
      <div class="stat-card net-worth">
        <p class="stat-label">净资产</p>
        <p class="stat-value">{{ formatCurrency(netWorthData.net_worth) }}</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">总资产</p>
        <p class="stat-value income">{{ formatCurrency(netWorthData.total_assets) }}</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">总负债</p>
        <p class="stat-value expense">{{ formatCurrency(netWorthData.total_liabilities) }}</p>
      </div>
      <div class="stat-card">
        <p class="stat-label">账户数量</p>
        <p class="stat-value">{{ accountStore.accounts.length }}</p>
      </div>
    </div>

    <!-- Accounts quick view -->
    <section class="section">
      <h2 class="section-title">我的账户</h2>
      <div class="account-grid">
        <div
          v-for="acc in accountStore.accounts"
          :key="acc.id"
          class="account-card"
        >
          <div class="account-name">{{ acc.name }}</div>
          <div class="account-type">{{ acc.account_type }}</div>
          <div class="account-balance">{{ formatCurrency(acc.balance, acc.currency) }}</div>
        </div>
        <div v-if="accountStore.accounts.length === 0 && !loading" class="empty-accounts">
          暂无账户，请先添加账户
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  box-shadow: var(--shadow-card);
}

.stat-card.net-worth {
  border-color: rgba(56, 189, 248, 0.3);
  background: linear-gradient(135deg, var(--color-bg-card), rgba(56, 189, 248, 0.05));
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-mono);
}

.stat-value.income { color: var(--color-income); }
.stat-value.expense { color: var(--color-expense); }

.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 14px;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.account-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px 18px;
}

.account-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.account-type {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 10px;
}

.account-balance {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-accent);
  font-family: var(--font-mono);
}

.empty-accounts {
  color: var(--color-text-muted);
  font-size: 14px;
  padding: 20px;
}
</style>
