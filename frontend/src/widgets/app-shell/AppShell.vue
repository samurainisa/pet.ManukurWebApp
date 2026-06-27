<template>
  <div class="min-h-screen lg:flex">
    <aside class="hidden w-72 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
      <div class="px-6 py-6">
        <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Nail Office</p>
        <h1 class="mt-2 text-xl font-bold text-slate-800">ManikurWebApp</h1>
      </div>

      <nav class="flex-1 space-y-1 px-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link px-4 py-2.5"
          active-class="bg-[var(--primary-soft)] text-[var(--primary)] font-semibold"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="border-t border-slate-100 p-4">
        <button class="btn-muted w-full" type="button" :disabled="isLoggingOut" @click="onLogout">
          {{ isLoggingOut ? 'Выход...' : 'Выйти' }}
        </button>
      </div>
    </aside>

    <div class="flex min-h-screen flex-1 flex-col">
      <header class="sticky top-0 z-20 border-b border-slate-200/70 bg-white/95 backdrop-blur">
        <div class="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-3 md:px-6">
          <div>
            <p class="text-xs uppercase tracking-[0.15em] text-slate-400">{{ cabinetLabel }}</p>
            <h2 class="text-lg font-semibold text-slate-800">{{ pageTitle }}</h2>
          </div>
          <button class="btn-muted lg:hidden" type="button" @click="mobileOpen = !mobileOpen">Меню</button>
        </div>
      </header>

      <div v-if="mobileOpen" class="space-y-1 border-b border-slate-200 bg-white px-3 py-3 lg:hidden">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link px-3 py-2"
          active-class="bg-[var(--primary-soft)] text-[var(--primary)] font-semibold"
          @click="mobileOpen = false"
        >
          {{ item.label }}
        </RouterLink>
      </div>

      <main class="mx-auto w-full max-w-7xl flex-1 px-4 py-5 md:px-6 md:py-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ROUTE_PATHS } from '@/app/router/paths'
import { useSessionStore } from '@/entities/session'

const sessionStore = useSessionStore()
const route = useRoute()
const router = useRouter()

const mobileOpen = ref(false)
const isLoggingOut = ref(false)

const masterNavItems = [
  { to: ROUTE_PATHS.dashboard, label: 'Дашборд' },
  { to: ROUTE_PATHS.clients, label: 'Клиенты' },
  { to: ROUTE_PATHS.services, label: 'Услуги' },
  { to: ROUTE_PATHS.schedule, label: 'Расписание' },
  { to: ROUTE_PATHS.analytics, label: 'Аналитика' },
  { to: ROUTE_PATHS.scheduleSettings, label: 'График' },
]

const clientNavItems = [
  { to: ROUTE_PATHS.clientBook, label: 'Записаться' },
  { to: ROUTE_PATHS.clientAppointments, label: 'Мои визиты' },
  { to: ROUTE_PATHS.clientNotifications, label: 'Уведомления' },
]

const role = computed(() => sessionStore.currentUser?.role || 'master')
const navItems = computed(() => (role.value === 'client' ? clientNavItems : masterNavItems))
const cabinetLabel = computed(() => (role.value === 'client' ? 'Кабинет клиента' : 'Кабинет мастера'))
const pageTitle = computed(() => String(route.meta.title || 'ManikurWebApp'))

async function onLogout() {
  isLoggingOut.value = true
  try {
    await sessionStore.logout()
  } finally {
    isLoggingOut.value = false
    router.push(ROUTE_PATHS.login)
  }
}
</script>
