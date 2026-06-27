import { createPinia } from 'pinia'

import { useSessionStore } from '@/entities/session'
import { httpClient } from '@/shared/api/HttpClient'
import { useToastStore } from '@/shared/model/toast-store'

export function createAppPinia() {
  return createPinia()
}

export function setupHttpClient(): void {
  const sessionStore = useSessionStore()
  const toastStore = useToastStore()

  httpClient.configure({
    getToken: () => sessionStore.token,
    onUnauthorized: () => sessionStore.clearSession(),
    pushErrorToast: (title, message) => toastStore.push({ type: 'error', title, message }),
  })
}
