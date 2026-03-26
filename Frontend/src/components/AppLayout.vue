<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/useAuthStore'
import {
  Odometer,
  Wallet,
  List,
  TrendCharts,
  CreditCard,
  PieChart,
  Aim,
  SwitchButton,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isCollapsed = ref(false)

const navItems = [
  { name: 'dashboard',    label: '总览',   icon: Odometer },
  { name: 'accounts',     label: '账户',   icon: Wallet },
  { name: 'transactions', label: '流水',   icon: List },
  { name: 'assets',       label: '资产',   icon: TrendCharts },
  { name: 'liabilities',  label: '负债',   icon: CreditCard },
  { name: 'budgets',      label: '预算',   icon: PieChart },
  { name: 'goals',        label: '目标',   icon: Aim },
  { name: 'statistics',   label: '统计',   icon: TrendCharts },
]

const activeMenu = computed(() => route.name as string)

async function handleLogout() {
  await authStore.doLogout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <span class="logo-icon">$</span>
        <span v-if="!isCollapsed" class="logo-text">Clash</span>
        <el-icon class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <component :is="isCollapsed ? 'Expand' : 'Fold'" />
        </el-icon>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name }"
          class="nav-item"
          :class="{ active: activeMenu === item.name }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div v-if="!isCollapsed" class="user-info">
          <span class="username">{{ authStore.user?.username ?? '—' }}</span>
        </div>
        <el-icon class="logout-btn" title="退出登录" @click="handleLogout">
          <SwitchButton />
        </el-icon>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background: var(--color-bg-primary);
  overflow: hidden;
}

.sidebar {
  display: flex;
  flex-direction: column;
  width: 220px;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  transition: width 0.25s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--color-border);
}

.logo-icon {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-accent);
  font-family: var(--font-mono);
  flex-shrink: 0;
  width: 32px;
  text-align: center;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: 0.05em;
  flex: 1;
}

.collapse-btn {
  cursor: pointer;
  color: var(--color-text-muted);
  margin-left: auto;
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: var(--color-accent);
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 8px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: rgba(56, 189, 248, 0.12);
  color: var(--color-accent);
}

.nav-label {
  flex: 1;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-top: 1px solid var(--color-border);
}

.user-info {
  flex: 1;
  overflow: hidden;
}

.username {
  font-size: 13px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 18px;
  flex-shrink: 0;
}

.logout-btn:hover {
  color: var(--color-danger);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
}
</style>
