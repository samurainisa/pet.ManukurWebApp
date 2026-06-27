import { httpClient } from '@/shared/api/HttpClient'

import type { Appointment, SlotsResponse } from '@/entities/appointment'

import { CLIENT_PORTAL_ROUTES } from './routes'
import type {
  ClientBookingPayload,
  ClientBookingsResponse,
  ClientNotificationsResponse,
} from '../model/types'

export class ClientPortalApi {
  getAvailableSlots(serviceId: number, date: string): Promise<SlotsResponse> {
    return httpClient.get<SlotsResponse>(
      `${CLIENT_PORTAL_ROUTES.availableSlots}?service_id=${serviceId}&date=${date}`,
    )
  }

  getBookings(): Promise<ClientBookingsResponse> {
    return httpClient.get<ClientBookingsResponse>(CLIENT_PORTAL_ROUTES.bookings)
  }

  createBooking(payload: ClientBookingPayload): Promise<Appointment> {
    return httpClient.post<Appointment>(CLIENT_PORTAL_ROUTES.bookings, payload)
  }

  getNotifications(): Promise<ClientNotificationsResponse> {
    return httpClient.get<ClientNotificationsResponse>(CLIENT_PORTAL_ROUTES.notifications)
  }
}

export const clientPortalApi = new ClientPortalApi()
