import type { PaymentMethod, PaymentStatus } from '@/shared/types/domain'

export type { PaymentMethod, PaymentStatus }

export interface Payment {
  id?: number
  appointment: number
  amount: string
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  paid_at: string | null
  comment: string | null
  created_at?: string
  updated_at?: string
}

export interface PaymentPayload {
  amount?: string
  payment_method?: PaymentMethod
  payment_status?: PaymentStatus
  paid_at?: string | null
  comment?: string | null
}
