export interface Service {
  id: number
  name: string
  description: string | null
  base_duration_min: number
  base_price: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ServicePayload {
  name?: string
  description?: string | null
  base_duration_min?: number
  base_price?: string
  is_active?: boolean
  sort_order?: number
}

export interface ServiceListParams {
  isActive?: boolean
}
