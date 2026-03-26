import service from './request'
import type { ApiResponse, Asset, PaginatedResponse } from '@/types'

export function getAssets() {
  return service.get<ApiResponse<Asset[]>>('/assets/')
}

export function getAsset(id: number) {
  return service.get<ApiResponse<Asset>>(`/assets/${id}/`)
}

export function createAsset(data: Partial<Asset>) {
  return service.post<ApiResponse<Asset>>('/assets/', data)
}

export function updateAsset(id: number, data: Partial<Asset>) {
  return service.put<ApiResponse<Asset>>(`/assets/${id}/`, data)
}

export function deleteAsset(id: number) {
  return service.delete<ApiResponse<null>>(`/assets/${id}/`)
}
