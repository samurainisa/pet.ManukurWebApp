import { httpClient } from '@/shared/api/HttpClient'

import { PAYMENT_ROUTES } from './routes'
import type { Payment, PaymentPayload } from '../model/types'

export class PaymentApi {
  getByAppointment(appointmentId: number): Promise<Payment> {
    return httpClient.get<Payment>(PAYMENT_ROUTES.byAppointment(appointmentId))
  }

  save(appointmentId: number, payload: PaymentPayload): Promise<Payment> {
    return httpClient.put<Payment>(PAYMENT_ROUTES.byAppointment(appointmentId), payload)
  }
}

export const paymentApi = new PaymentApi()
