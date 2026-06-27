export const PAYMENT_ROUTES = {
  byAppointment: (appointmentId: number) => `/appointments/${appointmentId}/payment/`,
} as const
