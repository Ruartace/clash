import service from './request'
import type { ApiResponse, Budget, PaginatedResponse } from '@/types'

export function getBudgets(month?: string) {
  return service.get<ApiResponse<PaginatedResponse<Budget>>>('/budgets/', {
    params: month ? { month } : undefined,
  })
}

export function createBudget(data: Partial<Budget>) {
  return service.post<ApiResponse<Budget>>('/budgets/', data)
}

export function updateBudget(id: number, data: Partial<Budget>) {
  return service.put<ApiResponse<Budget>>(`/budgets/${id}/`, data)
}

export function deleteBudget(id: number) {
  return service.delete<ApiResponse<null>>(`/budgets/${id}/`)
}
