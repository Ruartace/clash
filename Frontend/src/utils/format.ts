/**
 * Format a decimal string as CNY currency
 */
export function formatCurrency(value: string | number, currency = 'CNY'): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(num)
}

/**
 * Format ISO date string to YYYY-MM-DD
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return '—'
  return dateStr.slice(0, 10)
}

/**
 * Format ISO datetime string to YYYY-MM-DD HH:mm
 */
export function formatDateTime(dateStr: string): string {
  if (!dateStr) return '—'
  return dateStr.slice(0, 16).replace('T', ' ')
}

/**
 * Calculate percentage string, safe division
 */
export function formatPercent(value: string | number, total: string | number): string {
  const v = parseFloat(String(value))
  const t = parseFloat(String(total))
  if (isNaN(v) || isNaN(t) || t === 0) return '0%'
  return `${((v / t) * 100).toFixed(1)}%`
}

/**
 * Return abbreviated large numbers (e.g. 12000 → 1.2万)
 */
export function formatCompact(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '—'
  if (Math.abs(num) >= 1e8) return `${(num / 1e8).toFixed(2)}亿`
  if (Math.abs(num) >= 1e4) return `${(num / 1e4).toFixed(2)}万`
  return String(num)
}
