import service from './request'
import type { ApiResponse, Account, PaginatedResponse } from '@/types'

export function getAccounts() {
  return service.get<ApiResponse<PaginatedResponse<Account>>>('/accounts/')
}

export function getAccount(id: number) {
  return service.get<ApiResponse<Account>>(`/accounts/${id}/`)
}

export function createAccount(data: Partial<Account>) {
  return service.post<ApiResponse<Account>>('/accounts/', data)
}

export function updateAccount(id: number, data: Partial<Account>) {
  return service.put<ApiResponse<Account>>(`/accounts/${id}/`, data)
}

export function patchAccount(id: number, data: Partial<Account>) {
  return service.patch<ApiResponse<Account>>(`/accounts/${id}/`, data)
}
