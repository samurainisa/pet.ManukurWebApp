import type { AppointmentStatus, PaymentStatus } from '@/shared/types/domain'

export interface Client {
  id: number
  full_name: string
  phone: string
  email: string | null
  notes: string | null
  total_paid?: string
  created_at: string
  updated_at: string
}

export interface ClientHistoryItem {
  id: number
  status: AppointmentStatus
  start_datetime: string
  end_datetime: string
  planned_duration_min: number
  planned_price: string
  service_name: string
  payment_amount: string | null
  payment_status: PaymentStatus | null
  comment_master: string | null
}

export interface ClientHistoryResponse {
  client: Client
  history: ClientHistoryItem[]
  total_paid: string
  visits_count: number
}

export interface ClientPayload {
  full_name: string
  phone: string
  email?: string | null
  notes?: string | null
}

export interface ClientListParams {
  search?: string
  page?: number
}
