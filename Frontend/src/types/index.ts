// ─── Universal API Response Wrapper ───────────────────────────────────────
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ─── Auth / User ─────────────────────────────────────────────────────────────
export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password_confirm: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  date_joined: string
}

// ─── Account ─────────────────────────────────────────────────────────────────
export interface Account {
  id: number
  name: string
  account_type: string
  balance: string        // Decimal as string to avoid float precision loss
  currency: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ─── Transaction ─────────────────────────────────────────────────────────────
export type TransactionType = 'income' | 'expense' | 'transfer'

export interface Transaction {
  id: number
  account: number
  account_name: string
  transaction_type: TransactionType
  amount: string
  category: string
  description: string
  transaction_date: string
  created_at: string
  updated_at: string
}

// ─── Asset ───────────────────────────────────────────────────────────────────
export interface Asset {
  id: number
  name: string
  asset_type: string
  current_value: string
  purchase_price: string
  purchase_date: string
  description: string
  created_at: string
  updated_at: string
}

// ─── Liability ───────────────────────────────────────────────────────────────
export interface Liability {
  id: number
  name: string
  liability_type: string
  principal: string
  interest_rate: string
  monthly_payment: string
  due_date: string
  description: string
  created_at: string
  updated_at: string
}

// ─── Budget ──────────────────────────────────────────────────────────────────
export interface Budget {
  id: number
  category: string
  amount: string
  spent: string
  month: string          // YYYY-MM
  created_at: string
  updated_at: string
}

// ─── Goal ────────────────────────────────────────────────────────────────────
export interface Goal {
  id: number
  name: string
  target_amount: string
  current_amount: string
  deadline: string
  description: string
  is_completed: boolean
  created_at: string
  updated_at: string
}

// ─── Statistics ──────────────────────────────────────────────────────────────
export interface MonthlySummary {
  month: string
  income: string
  expense: string
  net: string
}

export interface CategoryBreakdown {
  category: string
  total: string
  percentage: string
}
