import { createRouter, createWebHistory } from 'vue-router'

import { registerRouterGuards } from './guards'
import { appRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes: appRoutes,
})

registerRouterGuards(router)

export default router
