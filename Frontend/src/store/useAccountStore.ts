import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAccounts } from '@/api/accounts'
import type { Account } from '@/types'

export const useAccountStore = defineStore('account', () => {
  const accounts = ref<Account[]>([])
  const loading = ref(false)

  async function fetchAccounts() {
    loading.value = true
    try {
      const res = await getAccounts()
      accounts.value = res.data.data.results
    } finally {
      loading.value = false
    }
  }

  return { accounts, loading, fetchAccounts }
})
