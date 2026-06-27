import type { ClientNotificationType } from '@/shared/types/domain'

import type { Appointment } from '@/entities/appointment'

export interface ClientBookingsResponse {
  items: Appointment[]
}

export interface ClientNotificationItem {
  appointment_id: number
  type: ClientNotificationType
  title: string
  message: string
  start_datetime: string | null
}

export interface ClientNotificationsResponse {
  items: ClientNotificationItem[]
}

export interface ClientBookingPayload {
  service_id: number
  date: string
  time: string
  comment?: string
}
