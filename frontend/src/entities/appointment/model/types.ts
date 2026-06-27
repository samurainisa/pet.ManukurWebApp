import type { AppointmentSource, AppointmentStatus, PaymentStatus } from '@/shared/types/domain'

import type { VisitPhoto } from '@/entities/visit'

export type { AppointmentStatus, AppointmentSource }

export interface Appointment {
  id: number
  client: number
  client_name: string
  client_phone: string
  service: number
  service_name: string
  status: AppointmentStatus
  source: AppointmentSource
  appointment_date: string
  start_datetime: string
  end_datetime: string
  planned_duration_min: number
  planned_price: string
  comment_client: string | null
  comment_master: string | null
  created_by: number | null
  needs_removal: boolean
  needs_strengthening: boolean
  design_notes: string | null
  payment_status: PaymentStatus | null
  photos?: VisitPhoto[]
  created_at: string
  updated_at: string
}

export interface CalendarDayResponse {
  date: string
  appointments: Appointment[]
}

export interface CalendarWeekDay {
  date: string
  appointments: Appointment[]
}

export interface CalendarWeekResponse {
  week_start: string
  week_end: string
  days: CalendarWeekDay[]
}

export interface SlotsResponse {
  service_id: number
  date: string
  slots: string[]
}

export interface WorkScheduleRule {
  id: number
  weekday: number
  start_time: string
  end_time: string
  is_working_day: boolean
}

export interface TimeOffBlock {
  id: number
  start_datetime: string
  end_datetime: string
  reason: string | null
  created_at: string
}

export interface AppointmentListParams extends Record<string, string | undefined> {}

export interface ReschedulePayload {
  start_datetime: string
  planned_duration_min: number
}

export interface CancelPayload {
  reason: string
}

export interface TimeOffPayload {
  start_datetime: string
  end_datetime: string
  reason: string | null
}
