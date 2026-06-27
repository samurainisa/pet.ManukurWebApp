import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { sessionApi } from '../api/SessionApi'
import type { LoginPayload, RegisterPayload, User } from '../model/types'

const TOKEN_STORAGE_KEY = 'auth_token'

export const useSessionStore = defineStore('session', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))
  const currentUser = ref<User | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))
  const role = computed(() => currentUser.value?.role ?? null)

  function setSession(nextToken: string, user: User): void {
    token.value = nextToken
    currentUser.value = user
    localStorage.setItem(TOKEN_STORAGE_KEY, nextToken)
  }

  function clearSession(): void {
    token.value = null
    currentUser.value = null
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }

  async function login(payload: LoginPayload) {
    const response = await sessionApi.login(payload)
    setSession(response.token, response.user)
    return response
  }

  async function register(payload: RegisterPayload) {
    const response = await sessionApi.register(payload)
    setSession(response.token, response.user)
    return response
  }

  async function logout() {
    try {
      await sessionApi.logout()
    } finally {
      clearSession()
    }
  }

  async function ensureUserLoaded(): Promise<User | null> {
    if (!token.value) {
      return null
    }

    if (currentUser.value) {
      return currentUser.value
    }

    const me = await sessionApi.fetchMe()
    currentUser.value = me
    return me
  }

  return {
    token,
    currentUser,
    isAuthenticated,
    role,
    setSession,
    clearSession,
    login,
    register,
    logout,
    ensureUserLoaded,
  }
})
