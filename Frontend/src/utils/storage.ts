const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export const storage = {
  getAccess: (): string | null => localStorage.getItem(ACCESS_KEY),
  setAccess: (token: string): void => localStorage.setItem(ACCESS_KEY, token),
  getRefresh: (): string | null => localStorage.getItem(REFRESH_KEY),
  setRefresh: (token: string): void => localStorage.setItem(REFRESH_KEY, token),
  setTokens: (access: string, refresh: string): void => {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clearTokens: (): void => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}
