import service from './request'
import type { ApiResponse, Liability, PaginatedResponse } from '@/types'

export function getLiabilities() {
  return service.get<ApiResponse<Liability[]>>('/liabilities/')
}

export function getLiability(id: number) {
  return service.get<ApiResponse<Liability>>(`/liabilities/${id}/`)
}

export function createLiability(data: Partial<Liability>) {
  return service.post<ApiResponse<Liability>>('/liabilities/', data)
}

export function updateLiability(id: number, data: Partial<Liability>) {
  return service.put<ApiResponse<Liability>>(`/liabilities/${id}/`, data)
}

export function deleteLiability(id: number) {
  return service.delete<ApiResponse<null>>(`/liabilities/${id}/`)
}
