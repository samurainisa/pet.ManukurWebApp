import type { Router } from 'vue-router'

import { useSessionStore, type UserRole } from '@/entities/session'

import { defaultPathByRole, ROUTE_PATHS } from './paths'

export function registerRouterGuards(router: Router): void {
  router.beforeEach(async (to) => {
    const sessionStore = useSessionStore()
    const requiresAuth = Boolean(to.meta.requiresAuth)

    if (sessionStore.token) {
      try {
        await sessionStore.ensureUserLoaded()
      } catch {
        sessionStore.clearSession()
      }
    }

    if (requiresAuth && !sessionStore.token) {
      return { path: ROUTE_PATHS.login }
    }

    const role = sessionStore.currentUser?.role
    const allowedRoles = Array.isArray(to.meta.roles) ? (to.meta.roles as UserRole[]) : null

    if (requiresAuth && allowedRoles && role && !allowedRoles.includes(role)) {
      return { path: defaultPathByRole(role) }
    }

    if ((to.path === ROUTE_PATHS.login || to.path === ROUTE_PATHS.register) && sessionStore.token) {
      return { path: defaultPathByRole(role) }
    }

    return true
  })
}
