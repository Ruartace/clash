import service from './request'
import type { ApiResponse, Transaction, PaginatedResponse } from '@/types'

export interface TransactionQuery {
  page?: number
  page_size?: number
  transaction_type?: string
  category?: string
  account?: number
  date_from?: string
  date_to?: string
}

export function getTransactions(params?: TransactionQuery) {
  return service.get<ApiResponse<PaginatedResponse<Transaction>>>('/transactions/', { params })
}

export function getTransaction(id: number) {
  return service.get<ApiResponse<Transaction>>(`/transactions/${id}/`)
}

export function createTransaction(data: Partial<Transaction>) {
  return service.post<ApiResponse<Transaction>>('/transactions/', data)
}

export function updateTransaction(id: number, data: Partial<Transaction>) {
  return service.put<ApiResponse<Transaction>>(`/transactions/${id}/`, data)
}

export function deleteTransaction(id: number) {
  return service.delete<ApiResponse<null>>(`/transactions/${id}/`)
}
