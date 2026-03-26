import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, getUserProfile, logout } from '@/api/auth'
import { storage } from '@/utils/storage'
import type { UserProfile, LoginPayload } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = ref<boolean>(!!storage.getAccess())

  async function doLogin(payload: LoginPayload) {
    const res = await login(payload)
    // simplejwt 直接返回 { access, refresh }，无外层 data 包装
    const { access, refresh } = res.data as unknown as { access: string; refresh: string }
    storage.setTokens(access, refresh)
    isAuthenticated.value = true
    await fetchProfile()
  }

  async function fetchProfile() {
    const res = await getUserProfile()
    user.value = res.data.data
  }

  async function doLogout() {
    try {
      await logout()
    } finally {
      storage.clearTokens()
      isAuthenticated.value = false
      user.value = null
    }
  }

  return { user, isAuthenticated, doLogin, doLogout, fetchProfile }
})
