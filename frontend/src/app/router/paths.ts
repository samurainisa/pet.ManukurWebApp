import type { UserRole } from '@/entities/session'

export const ROUTE_PATHS = {
  login: '/login',
  register: '/register',
  book: '/book',
  bookSuccess: '/book/success',
  dashboard: '/dashboard',
  clients: '/clients',
  clientDetail: '/clients/:id',
  services: '/services',
  schedule: '/schedule',
  appointmentDetail: '/appointments/:id',
  analytics: '/analytics',
  scheduleSettings: '/settings/schedule',
  clientBook: '/client/book',
  clientAppointments: '/client/appointments',
  clientNotifications: '/client/notifications',
} as const

export function defaultPathByRole(role: UserRole | null | undefined): string {
  return role === 'client' ? ROUTE_PATHS.clientBook : ROUTE_PATHS.dashboard
}

export function clientDetailPath(id: number): string {
  return `/clients/${id}`
}

export function appointmentDetailPath(id: number): string {
  return `/appointments/${id}`
}
