import { httpClient } from '@/shared/api/HttpClient'

import { PUBLIC_BOOKING_ROUTES } from './routes'
import type { PublicBookingPayload, PublicBookingSuccess, PublicLanding } from '../model/types'

export class PublicBookingApi {
  getLanding(): Promise<PublicLanding> {
    return httpClient.get<PublicLanding>(PUBLIC_BOOKING_ROUTES.profile, { withAuth: false })
  }

  createBooking(payload: PublicBookingPayload): Promise<PublicBookingSuccess> {
    return httpClient.post<PublicBookingSuccess>(PUBLIC_BOOKING_ROUTES.bookings, payload, {
      withAuth: false,
    })
  }
}

export const publicBookingApi = new PublicBookingApi()
