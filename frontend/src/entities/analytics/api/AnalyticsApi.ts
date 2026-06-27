import { httpClient } from '@/shared/api/HttpClient'

import {
  analyticsRevenueUrl,
  analyticsServicesUrl,
  analyticsSummaryUrl,
  analyticsVisitsUrl,
} from './routes'
import type {
  AnalyticsPeriodParams,
  AnalyticsRevenueResponse,
  AnalyticsServicesResponse,
  AnalyticsSummary,
  AnalyticsVisitsResponse,
} from '../model/types'

export class AnalyticsApi {
  getSummary({ dateFrom, dateTo }: AnalyticsPeriodParams): Promise<AnalyticsSummary> {
    return httpClient.get<AnalyticsSummary>(analyticsSummaryUrl(dateFrom, dateTo))
  }

  getServices({ dateFrom, dateTo }: AnalyticsPeriodParams): Promise<AnalyticsServicesResponse> {
    return httpClient.get<AnalyticsServicesResponse>(analyticsServicesUrl(dateFrom, dateTo))
  }

  getVisits({ dateFrom, dateTo }: AnalyticsPeriodParams): Promise<AnalyticsVisitsResponse> {
    return httpClient.get<AnalyticsVisitsResponse>(analyticsVisitsUrl(dateFrom, dateTo))
  }

  getRevenue({ dateFrom, dateTo }: AnalyticsPeriodParams): Promise<AnalyticsRevenueResponse> {
    return httpClient.get<AnalyticsRevenueResponse>(analyticsRevenueUrl(dateFrom, dateTo))
  }
}

export const analyticsApi = new AnalyticsApi()
