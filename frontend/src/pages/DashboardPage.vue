<template>
  <section class="space-y-6">
    <PageHeader title="Дашборд" subtitle="Сводка по записи, отменам и ближайшим визитам" />

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Записей за сегодня" :value="summary?.today_count ?? '-'" />
      <StatCard label="Записей за период" :value="summary?.visits_count ?? '-'" />
      <StatCard label="Отмены" :value="summary?.cancelled_count ?? '-'" />
      <StatCard label="Неявки" :value="summary?.no_show_count ?? '-'" />
    </div>

    <div class="grid gap-4 lg:grid-cols-3">
      <RouterLink to="/schedule" class="card block transition hover:-translate-y-0.5 hover:shadow-lg">
        <p class="text-sm text-slate-500">Быстрое действие</p>
        <p class="mt-2 text-lg font-semibold text-slate-800">Новая запись</p>
      </RouterLink>
      <RouterLink to="/clients" class="card block transition hover:-translate-y-0.5 hover:shadow-lg">
        <p class="text-sm text-slate-500">Быстрое действие</p>
        <p class="mt-2 text-lg font-semibold text-slate-800">Новый клиент</p>
      </RouterLink>
      <RouterLink to="/services" class="card block transition hover:-translate-y-0.5 hover:shadow-lg">
        <p class="text-sm text-slate-500">Быстрое действие</p>
        <p class="mt-2 text-lg font-semibold text-slate-800">Новая услуга</p>
      </RouterLink>
    </div>

    <LoadingBlock v-if="loading" text="Загружаю данные дашборда..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <div v-else class="grid gap-4 xl:grid-cols-2">
      <article class="card">
        <h2 class="text-lg font-semibold text-slate-800">Сегодняшние записи</h2>
        <div v-if="todayAppointments.length" class="mt-4 space-y-3">
          <div
            v-for="appointment in todayAppointments"
            :key="appointment.id"
            class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2"
          >
            <div class="flex items-center justify-between gap-3">
              <p class="font-semibold text-slate-800">{{ appointment.client_name }}</p>
              <StatusBadge :status="appointment.status" />
            </div>
            <p class="mt-1 text-sm text-slate-500">{{ appointment.service_name }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ formatDateTime(appointment.start_datetime) }}</p>
          </div>
        </div>
        <EmptyState
          v-else
          title="На сегодня записей нет"
          description="Создайте новую запись через раздел расписания."
          class="mt-4"
        />
      </article>

      <article class="card">
        <h2 class="text-lg font-semibold text-slate-800">Ближайшие записи</h2>
        <div v-if="upcomingAppointments.length" class="mt-4 space-y-3">
          <div
            v-for="appointment in upcomingAppointments"
            :key="appointment.id"
            class="rounded-xl border border-slate-100 px-3 py-2"
          >
            <div class="flex items-center justify-between gap-3">
              <p class="font-semibold text-slate-800">{{ appointment.client_name }}</p>
              <p class="text-xs text-slate-400">{{ formatDateTime(appointment.start_datetime) }}</p>
            </div>
            <p class="mt-1 text-sm text-slate-500">{{ appointment.service_name }}</p>
          </div>
        </div>
        <EmptyState
          v-else
          title="Нет ближайших визитов"
          description="Расписание пока свободно."
          class="mt-4"
        />
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { analyticsApi } from '@/entities/analytics'
import type { AnalyticsSummary } from '@/entities/analytics/model/types'
import { appointmentApi } from '@/entities/appointment'
import type { Appointment } from '@/entities/appointment'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatCard from '@/shared/ui/StatCard.vue'
import StatusBadge from '@/shared/ui/StatusBadge.vue'
import { formatDateTime, toDateInputValue } from '@/shared/lib/format'

const loading = ref(true)
const error = ref('')
const summary = ref<AnalyticsSummary | null>(null)
const todayAppointments = ref<Appointment[]>([])
const upcomingAppointments = ref<Appointment[]>([])

async function loadDashboard() {
  loading.value = true
  error.value = ''

  const today = new Date()
  const dateTo = toDateInputValue(today)
  const dateFrom = toDateInputValue(new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000))

  try {
    const [summaryRes, todayRes, upcomingRes] = await Promise.all([
      analyticsApi.getSummary({ dateFrom, dateTo }),
      appointmentApi.getList({ date_from: dateTo, date_to: dateTo }),
      appointmentApi.getList({ date_from: dateTo }),
    ])

    summary.value = summaryRes
    todayAppointments.value = todayRes.results
    upcomingAppointments.value = upcomingRes.results.slice(0, 8)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить дашборд'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>