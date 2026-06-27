import { httpClient } from '@/shared/api/HttpClient'
import type { PaginatedResponse } from '@/shared/types/pagination'

import { CLIENT_ROUTES } from './routes'
import type {
  Client,
  ClientHistoryResponse,
  ClientListParams,
  ClientPayload,
} from '../model/types'

export class ClientApi {
  getList(params: ClientListParams = {}): Promise<PaginatedResponse<Client>> {
    const query = new URLSearchParams()
    if (params.search) {
      query.set('search', params.search)
    }
    if (params.page) {
      query.set('page', String(params.page))
    }

    const suffix = query.toString()
    return httpClient.get<PaginatedResponse<Client>>(
      suffix ? `${CLIENT_ROUTES.list}?${suffix}` : CLIENT_ROUTES.list,
    )
  }

  create(payload: ClientPayload): Promise<Client> {
    return httpClient.post<Client>(CLIENT_ROUTES.list, payload)
  }

  update(id: number, payload: Partial<ClientPayload>): Promise<Client> {
    return httpClient.patch<Client>(CLIENT_ROUTES.detail(id), payload)
  }

  getHistory(id: number): Promise<ClientHistoryResponse> {
    return httpClient.get<ClientHistoryResponse>(CLIENT_ROUTES.history(id))
  }
}

export const clientApi = new ClientApi()
