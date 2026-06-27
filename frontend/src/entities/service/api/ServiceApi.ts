import { httpClient } from '@/shared/api/HttpClient'
import type { PaginatedResponse } from '@/shared/types/pagination'

import { SERVICE_ROUTES } from './routes'
import type { Service, ServiceListParams, ServicePayload } from '../model/types'

export class ServiceApi {
  getList(params: ServiceListParams = {}): Promise<PaginatedResponse<Service>> {
    const query = new URLSearchParams()
    if (typeof params.isActive === 'boolean') {
      query.set('is_active', String(params.isActive))
    }

    const suffix = query.toString()
    return httpClient.get<PaginatedResponse<Service>>(
      suffix ? `${SERVICE_ROUTES.list}?${suffix}` : SERVICE_ROUTES.list,
    )
  }

  create(payload: ServicePayload): Promise<Service> {
    return httpClient.post<Service>(SERVICE_ROUTES.list, payload)
  }

  update(id: number, payload: ServicePayload): Promise<Service> {
    return httpClient.patch<Service>(SERVICE_ROUTES.detail(id), payload)
  }

  delete(id: number): Promise<null> {
    return httpClient.delete<null>(SERVICE_ROUTES.detail(id))
  }

  getPublicList(): Promise<PaginatedResponse<Service>> {
    return httpClient.get<PaginatedResponse<Service>>(SERVICE_ROUTES.publicList, { withAuth: false })
  }
}

export const serviceApi = new ServiceApi()
