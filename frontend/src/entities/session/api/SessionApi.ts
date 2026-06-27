import { httpClient } from '@/shared/api/HttpClient'

import { SESSION_ROUTES } from './routes'
import type {
  AuthResponse,
  LoginPayload,
  LogoutResponse,
  RegisterPayload,
  User,
} from '../model/types'

export class SessionApi {
  login(payload: LoginPayload): Promise<AuthResponse> {
    return httpClient.post<AuthResponse>(SESSION_ROUTES.login, payload, { withAuth: false })
  }

  register(payload: RegisterPayload): Promise<AuthResponse> {
    return httpClient.post<AuthResponse>(SESSION_ROUTES.register, payload, { withAuth: false })
  }

  logout(): Promise<LogoutResponse> {
    return httpClient.post<LogoutResponse>(SESSION_ROUTES.logout)
  }

  fetchMe(): Promise<User> {
    return httpClient.get<User>(SESSION_ROUTES.me)
  }
}

export const sessionApi = new SessionApi()
