export interface VisitResult {
  id: number
  appointment: number
  actual_service_summary: string | null
  materials_used: string | null
  result_notes: string | null
  actual_duration_min: number | null
  created_at: string
  updated_at: string
}

export interface VisitPhoto {
  id: number
  appointment: number
  image: string
  sort_order: number
  created_at: string
}

export interface VisitResultPayload {
  actual_service_summary?: string | null
  materials_used?: string | null
  result_notes?: string | null
  actual_duration_min?: number | null
}
