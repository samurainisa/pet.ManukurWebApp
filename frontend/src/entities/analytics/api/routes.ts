export const ANALYTICS_ROUTES = {
  summary: '/analytics/summary/',
  services: '/analytics/services/',
  visits: '/analytics/visits/',
  revenue: '/analytics/revenue/',
} as const

function periodQuery(dateFrom: string, dateTo: string): string {
  return `?date_from=${dateFrom}&date_to=${dateTo}`
}

export function analyticsSummaryUrl(dateFrom: string, dateTo: string): string {
  return `${ANALYTICS_ROUTES.summary}${periodQuery(dateFrom, dateTo)}`
}

export function analyticsServicesUrl(dateFrom: string, dateTo: string): string {
  return `${ANALYTICS_ROUTES.services}${periodQuery(dateFrom, dateTo)}`
}

export function analyticsVisitsUrl(dateFrom: string, dateTo: string): string {
  return `${ANALYTICS_ROUTES.visits}${periodQuery(dateFrom, dateTo)}`
}

export function analyticsRevenueUrl(dateFrom: string, dateTo: string): string {
  return `${ANALYTICS_ROUTES.revenue}${periodQuery(dateFrom, dateTo)}`
}
