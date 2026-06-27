import type { AppointmentStatus } from '@/shared/types/domain'

import type { Service } from '@/entities/service'

export interface PublicBookingPayload {
  service_id: number
  date: string
  time: string
  full_name: string
  phone: string
  comment: string
  website: string
}

export interface PublicBookingSuccess {
  id: number
  status: AppointmentStatus
  start_datetime: string
  end_datetime: string
  appointment_date: string
}

export interface PublicMasterProfile {
  display_name: string
  city: string | null
  address: string | null
  phone: string | null
  bio: string | null
  telegram: string | null
  avatar: string | null
}

export interface PublicReview {
  id: number
  client_name: string
  rating: number
  text: string
  created_at: string
}

export interface PublicPortfolioItem {
  id: number
  image: string | null
  service_name: string
  created_at: string
}

export interface PublicLanding {
  master: PublicMasterProfile
  rating_avg: number
  reviews_count: number
  reviews: PublicReview[]
  portfolio: PublicPortfolioItem[]
  services: Service[]
}
