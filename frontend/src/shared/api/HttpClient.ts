import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'

import { env } from '@/shared/config/env'

import { ApiError } from './ApiError'
import { getBackendErrorMessage } from './parse-api-error'

export interface HttpRequestConfig extends Omit<AxiosRequestConfig, 'auth'> {
  withAuth?: boolean
  toastOnError?: boolean
}

interface HttpClientHandlers {
  getToken: () => string | null
  onUnauthorized: () => void
  pushErrorToast: (title: string, message: string) => void
}

type RequestConfigWithFlags = InternalAxiosRequestConfig & {
  withAuth?: boolean
  toastOnError?: boolean
}

export class HttpClient {
  private static instance: HttpClient | null = null

  private readonly axios: AxiosInstance
  private handlers: HttpClientHandlers | null = null
  private configured = false

  private constructor() {
    this.axios = axios.create({
      baseURL: env.apiBaseUrl,
    })
  }

  static getInstance(): HttpClient {
    HttpClient.instance ??= new HttpClient()
    return HttpClient.instance
  }

  configure(handlers: HttpClientHandlers): void {
    this.handlers = handlers

    if (this.configured) {
      return
    }

    this.configured = true
    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    this.axios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      const flags = config as RequestConfigWithFlags
      const useAuth = flags.withAuth !== false
      const token = useAuth ? this.handlers?.getToken() ?? null : null

      if (token) {
        config.headers.set('Authorization', `Token ${token}`)
      }

      const isFormData = typeof FormData !== 'undefined' && config.data instanceof FormData
      if (isFormData) {
        config.headers.delete('Content-Type')
      } else if (!config.headers.has('Content-Type')) {
        config.headers.set('Content-Type', 'application/json')
      }

      return config
    })

    this.axios.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const flags = error.config as RequestConfigWithFlags | undefined
        const toastOnError = flags?.toastOnError !== false

        if (!error.response) {
          const message = 'Ошибка сети. Проверьте подключение к backend.'
          if (toastOnError) {
            this.handlers?.pushErrorToast('Ошибка соединения', message)
          }
          return Promise.reject(new ApiError(message, 0))
        }

        const { status, data } = error.response

        if (status === 401) {
          this.handlers?.onUnauthorized()
        }

        const message = getBackendErrorMessage(data)
        if (toastOnError) {
          this.handlers?.pushErrorToast(`Ошибка ${status}`, message)
        }

        return Promise.reject(new ApiError(message, status, data))
      },
    )
  }

  async request<T>(config: HttpRequestConfig): Promise<T> {
    const response = await this.axios.request<T>(config)
    return response.data
  }

  get<T>(url: string, config?: HttpRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'GET', url })
  }

  post<T>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'POST', url, data })
  }

  put<T>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'PUT', url, data })
  }

  patch<T>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'PATCH', url, data })
  }

  delete<T>(url: string, config?: HttpRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'DELETE', url })
  }
}

export const httpClient = HttpClient.getInstance()
