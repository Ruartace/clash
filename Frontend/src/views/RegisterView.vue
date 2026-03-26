<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import { storage } from '@/utils/storage'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})

async function handleRegister() {
  if (!form.username || !form.email || !form.password || !form.password_confirm) {
    ElMessage.warning('请填写所有字段')
    return
  }
  if (form.password !== form.password_confirm) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  if (form.password.length < 8) {
    ElMessage.warning('密码长度不能少于 8 位')
    return
  }
  loading.value = true
  try {
    const res = await register({
      username: form.username,
      email: form.email,
      password: form.password,
      password_confirm: form.password_confirm,
    })
    const { access, refresh } = res.data.data
    storage.setTokens(access, refresh)
    authStore.isAuthenticated = true
    await authStore.fetchProfile()
    ElMessage.success('注册成功，欢迎加入 Clash！')
    router.push({ name: 'dashboard' })
  } catch (err: unknown) {
    const e = err as { response?: { data?: { data?: Record<string, string[]> } } }
    const errors = e?.response?.data?.data
    if (errors) {
      const first = Object.values(errors)[0]
      ElMessage.error(Array.isArray(first) ? first[0] : String(first))
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="login-bg">
      <div class="grid-overlay" />
    </div>

    <div class="register-card">
      <div class="brand">
        <span class="brand-symbol">$</span>
        <h1 class="brand-name">Clash</h1>
        <p class="brand-tagline">创建您的账户</p>
      </div>

      <el-form :model="form" class="register-form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="'User'"
            autocomplete="username"
          />
        </el-form-item>
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
            placeholder="密码（至少 8 位）"
            size="large"
            :prefix-icon="'Lock'"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password_confirm"
            type="password"
            placeholder="确认密码"
            size="large"
            :prefix-icon="'Lock'"
            show-password
            autocomplete="new-password"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="register-btn"
          :loading="loading"
          @click="handleRegister"
        >
          注 册
        </el-button>
      </el-form>

      <p class="login-link">
        已有账户？
        <router-link :to="{ name: 'login' }">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
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

.register-card {
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.register-btn {
  width: 100%;
  margin-top: 8px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.1em;
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #0f172a;
}

.register-btn:hover {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.login-link a {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
