<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/useAuthStore'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

async function handleLogin() {
  if (!form.email || !form.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  loading.value = true
  try {
    await authStore.doLogin(form)
    router.push({ name: 'dashboard' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="grid-overlay" />
    </div>

    <div class="login-card">
      <div class="brand">
        <span class="brand-symbol">$</span>
        <h1 class="brand-name">Clash</h1>
        <p class="brand-tagline">个人现金流与资产管理</p>
      </div>

      <el-form :model="form" class="login-form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.email"
            placeholder="邮箱"
            size="large"
            :prefix-icon="'Message'"
            autocomplete="email"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="'Lock'"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <p class="register-link">
        没有账户？
        <router-link :to="{ name: 'register' }">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-primary);
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(56, 189, 248, 0.15) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 90% 90%, rgba(129, 140, 248, 0.1) 0%, transparent 60%);
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--color-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--color-border) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.3;
}

.login-card {
  position: relative;
  z-index: 1;
  width: 400px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  box-shadow: var(--shadow-card), 0 0 80px rgba(56, 189, 248, 0.06);
  animation: card-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand {
  text-align: center;
  margin-bottom: 36px;
}

.brand-symbol {
  display: inline-block;
  font-size: 40px;
  font-weight: 900;
  color: var(--color-accent);
  font-family: var(--font-mono);
  line-height: 1;
  margin-bottom: 8px;
}

.brand-name {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.brand-tagline {
  font-size: 13px;
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.1em;
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #0f172a;
}

.login-btn:hover {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.register-link {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.register-link a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
