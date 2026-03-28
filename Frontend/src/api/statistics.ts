import service from './request'
import type {
  ApiResponse,
  AssetNetworkData,
  CategoryBreakdown,
  FlowGraphData,
  FlowRecord,
  HeatmapMode,
  HeatmapPoint,
  MonthlySummary,
} from '@/types'

export function getMonthlySummary(year?: number) {
  return service.get<ApiResponse<MonthlySummary[]>>('/statistics/monthly/', {
    params: year ? { year } : undefined,
  })
}

export function getCategoryBreakdown(params?: { year?: number; month?: number }) {
  return service.get<ApiResponse<CategoryBreakdown[]>>('/statistics/expense-by-category/', { params })
}

export function getNetWorth() {
  return service.get<ApiResponse<{ net_worth: string; total_assets: string; total_liabilities: string }>>(
    '/statistics/net-worth/',
  )
}

export function getFlowRecords(params?: { year?: number; month?: number }) {
  return service.get<ApiResponse<FlowRecord[]>>('/statistics/flow-records/', { params })
}

export function createFlowRecord(payload: {
  source_name: string
  source_type: 'income' | 'account' | 'expense' | 'asset' | 'liability' | 'goal'
  target_name: string
  target_type: 'income' | 'account' | 'expense' | 'asset' | 'liability' | 'goal'
  amount: string
  flow_date?: string
  description?: string
}) {
  return service.post<ApiResponse<FlowRecord>>('/statistics/flow-records/', payload)
}

export function getFlowGraph(params?: { year?: number; month?: number }) {
  return service.get<ApiResponse<FlowGraphData>>('/statistics/flow-graph/', { params })
}

export function getHeatmapData(params: { year: number; mode: HeatmapMode }) {
  return service.get<ApiResponse<HeatmapPoint[]>>('/statistics/heatmap/', { params })
}

export function getAssetNetwork() {
  return service.get<ApiResponse<AssetNetworkData>>('/statistics/asset-network/')
}
