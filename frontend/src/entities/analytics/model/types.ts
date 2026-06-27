export interface AnalyticsSummary {
  date_from: string
  date_to: string
  visits_count: number
  cancelled_count: number
  no_show_count: number
  revenue: string
  today_count: number
  upcoming_count: number
}

export interface AnalyticsServiceRow {
  service_id: number
  service__name: string
  count: number
  planned_revenue: string
}

export interface AnalyticsServicesResponse {
  items: AnalyticsServiceRow[]
}

export interface AnalyticsVisitRow {
  client_id: number
  client__full_name: string
  client__phone: string
  visits_count: number
}

export interface AnalyticsVisitsResponse {
  all_clients: AnalyticsVisitRow[]
  repeat_clients: AnalyticsVisitRow[]
}

export interface AnalyticsRevenueRow {
  day: string
  total: string
}

export interface AnalyticsRevenueResponse {
  items: AnalyticsRevenueRow[]
}

export interface AnalyticsPeriodParams {
  dateFrom: string
  dateTo: string
}
