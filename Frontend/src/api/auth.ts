import service from './request'
import type { ApiResponse, LoginPayload, RegisterPayload, TokenPair, UserProfile } from '@/types'

export function login(payload: LoginPayload) {
  return service.post<ApiResponse<TokenPair>>('/auth/login/', payload)
}

export function register(payload: RegisterPayload) {
  return service.post<ApiResponse<UserProfile>>('/auth/register/', payload)
}

export function refreshToken(refresh: string) {
  return service.post<ApiResponse<{ access: string }>>('/auth/token/refresh/', { refresh })
}

export function getUserProfile() {
  return service.get<ApiResponse<UserProfile>>('/auth/me/')
}

export function logout() {
  const refresh = localStorage.getItem('refresh_token')
  return service.post('/auth/logout/', { refresh })
}
