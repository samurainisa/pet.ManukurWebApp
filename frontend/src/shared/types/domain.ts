export type AppointmentStatus =
  | 'created'
  | 'confirmed'
  | 'completed'
  | 'cancelled'
  | 'rescheduled'
  | 'no_show'

export type AppointmentSource = 'master_manual' | 'public_booking'

export type PaymentMethod = 'cash' | 'transfer' | 'card_manual'

export type PaymentStatus = 'unpaid' | 'paid' | 'partial'

export type ToastType = 'success' | 'error' | 'info'

export type ClientNotificationType = 'info' | 'warning' | 'success'
