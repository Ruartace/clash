import service from './request'
import type { ApiResponse, Goal, PaginatedResponse } from '@/types'

export function getGoals() {
  return service.get<ApiResponse<PaginatedResponse<Goal>>>('/goals/')
}

export function getGoal(id: number) {
  return service.get<ApiResponse<Goal>>(`/goals/${id}/`)
}

export function createGoal(data: Partial<Goal>) {
  return service.post<ApiResponse<Goal>>('/goals/', data)
}

export function updateGoal(id: number, data: Partial<Goal>) {
  return service.put<ApiResponse<Goal>>(`/goals/${id}/`, data)
}

export function deleteGoal(id: number) {
  return service.delete<ApiResponse<null>>(`/goals/${id}/`)
}
