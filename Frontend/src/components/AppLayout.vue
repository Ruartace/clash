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
  Share,
  Sunny,
  Connection,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isCollapsed = ref(false)

const navItems = [
  { name: 'dashboard',    label: '总览',     icon: Odometer,    group: 'main' },
  { name: 'accounts',     label: '账户',     icon: Wallet,      group: 'main' },
  { name: 'transactions', label: '流水',     icon: List,        group: 'main' },
  { name: 'assets',       label: '资产',     icon: TrendCharts, group: 'main' },
  { name: 'liabilities',  label: '负债',     icon: CreditCard,  group: 'main' },
  { name: 'budgets',      label: '预算',     icon: PieChart,    group: 'main' },
  { name: 'goals',        label: '目标',     icon: Aim,         group: 'main' },
  { name: 'statistics',   label: '统计',     icon: TrendCharts, group: 'main' },
  { name: 'flow',         label: '资金流向', icon: Share,       group: 'viz'  },
  { name: 'heatmap',      label: '热力图',   icon: Sunny,       group: 'viz'  },
  { name: 'network',      label: '资产网络', icon: Connection,  group: 'viz'  },
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
        <template v-for="(item, idx) in navItems" :key="item.name">
          <!-- Section divider before first viz item -->
          <div
            v-if="item.group === 'viz' && (idx === 0 || navItems[idx - 1].group !== 'viz')"
            class="nav-divider"
          >
            <span v-if="!isCollapsed" class="divider-label">可视化观测</span>
            <span v-else class="divider-line" />
          </div>
          <router-link
            :to="{ name: item.name }"
            class="nav-item"
            :class="{ active: activeMenu === item.name, 'viz-item': item.group === 'viz' }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </router-link>
        </template>
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
  gap: 2px;
  padding: 12px 8px;
  overflow-y: auto;
}

/* Scrollbar styling */
.sidebar-nav::-webkit-scrollbar {
  width: 3px;
}
.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}

.nav-divider {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 4px 6px;
  min-height: 20px;
}

.divider-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-accent-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  white-space: nowrap;
  flex: 1;
  border-top: 1px solid var(--color-border-gold);
  padding-top: 8px;
}

.divider-line {
  display: block;
  width: 100%;
  height: 1px;
  background: var(--color-border-gold);
  opacity: 0.5;
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
  background: var(--color-accent-subtle);
  color: var(--color-accent);
}

/* Viz items get a subtly different accent on active */
.nav-item.viz-item.active {
  background: rgba(200, 173, 126, 0.13);
  color: var(--color-accent);
  box-shadow: inset 2px 0 0 var(--color-accent);
}

.nav-item.viz-item:not(.active):hover {
  background: var(--color-bg-hover);
  color: var(--color-accent-hover);
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
