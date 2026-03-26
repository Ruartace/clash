import service from './request'
import type { ApiResponse, MonthlySummary, CategoryBreakdown } from '@/types'

export function getMonthlySummary(year?: number) {
  return service.get<ApiResponse<MonthlySummary[]>>('/statistics/monthly/', {
    params: year ? { year } : undefined,
  })
}

export function getCategoryBreakdown(params?: { month?: string; transaction_type?: string }) {
  return service.get<ApiResponse<CategoryBreakdown[]>>('/statistics/category/', { params })
}

export function getNetWorth() {
  return service.get<ApiResponse<{ net_worth: string; total_assets: string; total_liabilities: string }>>(
    '/statistics/net-worth/',
  )
}
