<template>
  <section class="space-y-6">
    <PageHeader title="Аналитика" subtitle="Визиты, отмены, неявки, выручка и востребованные услуги" />

    <div class="card flex flex-wrap items-end gap-3">
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Период с</label>
        <input v-model="dateFrom" class="input" type="date" />
      </div>
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">По</label>
        <input v-model="dateTo" class="input" type="date" />
      </div>
      <button class="btn-primary" type="button" @click="loadAnalytics" :disabled="loading">
        {{ loading ? 'Обновление...' : 'Обновить аналитику' }}
      </button>
    </div>

    <LoadingBlock v-if="loading" text="Собираю аналитику..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <template v-else>
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Визитов" :value="summary?.visits_count ?? '-'" />
        <StatCard label="Отмен" :value="summary?.cancelled_count ?? '-'" />
        <StatCard label="Неявок" :value="summary?.no_show_count ?? '-'" />
        <StatCard label="Выручка" :value="summary ? formatMoney(summary.revenue) : '-'" />
      </div>

      <div class="grid gap-4 xl:grid-cols-2">
        <article class="card">
          <h3 class="text-lg font-semibold text-slate-800">Топ услуг по записям</h3>
          <EmptyState
            v-if="servicesData.length === 0"
            class="mt-4"
            title="Недостаточно данных"
            description="Появится после добавления записей."
          />

          <div v-else class="mt-4 space-y-3">
            <div v-for="item in servicesData.slice(0, 8)" :key="item.service_id" class="space-y-1">
              <div class="flex items-center justify-between text-sm text-slate-600">
                <span>{{ item.service__name }}</span>
                <span>{{ item.count }} шт.</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-teal-400 to-cyan-500"
                  :style="{ width: `${Math.max(8, (item.count / maxServiceCount) * 100)}%` }"
                />
              </div>
            </div>
          </div>
        </article>

        <article class="card">
          <h3 class="text-lg font-semibold text-slate-800">Выручка по дням</h3>
          <EmptyState
            v-if="revenueData.length === 0"
            class="mt-4"
            title="Нет оплат за период"
            description="После фиксации оплат данные появятся здесь."
          />

          <div v-else class="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4">
            <div v-for="row in revenueData" :key="row.day" class="rounded-xl bg-slate-50 p-2 text-center">
              <p class="text-[11px] text-slate-500">{{ row.day }}</p>
              <div class="mx-auto mt-2 flex h-24 w-8 items-end rounded bg-slate-100">
                <div
                  class="w-full rounded bg-gradient-to-t from-emerald-400 to-emerald-300"
                  :style="{ height: `${Math.max(6, (Number(row.total) / maxRevenue) * 100)}%` }"
                />
              </div>
              <p class="mt-2 text-xs font-semibold text-slate-700">{{ formatMoney(row.total) }}</p>
            </div>
          </div>
        </article>
      </div>

      <article class="card">
        <h3 class="text-lg font-semibold text-slate-800">Повторные визиты</h3>

        <EmptyState
          v-if="repeatClients.length === 0"
          class="mt-4"
          title="Повторных визитов не найдено"
          description="Система покажет клиентов с 2+ визитами за период."
        />

        <div v-else class="mt-4 overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-500">
                <th class="px-3 py-2">Клиент</th>
                <th class="px-3 py-2">Телефон</th>
                <th class="px-3 py-2">Визиты</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in repeatClients" :key="row.client_id" class="border-b border-slate-100">
                <td class="px-3 py-2 font-medium text-slate-700">{{ row.client__full_name }}</td>
                <td class="px-3 py-2 text-slate-500">{{ row.client__phone }}</td>
                <td class="px-3 py-2 text-slate-600">{{ row.visits_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { analyticsApi } from '@/entities/analytics'
import type {
  AnalyticsRevenueRow,
  AnalyticsServiceRow,
  AnalyticsSummary,
  AnalyticsVisitRow,
} from '@/entities/analytics/model/types'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatCard from '@/shared/ui/StatCard.vue'
import { formatMoney, toDateInputValue } from '@/shared/lib/format'
import { validateDateRange } from '@/shared/lib/validation'

const today = new Date()
const toastStore = useToastStore()

const dateTo = ref(toDateInputValue(today))
const dateFrom = ref(toDateInputValue(new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000)))

const loading = ref(true)
const error = ref('')
const summary = ref<AnalyticsSummary | null>(null)
const servicesData = ref<AnalyticsServiceRow[]>([])
const revenueData = ref<AnalyticsRevenueRow[]>([])
const repeatClients = ref<AnalyticsVisitRow[]>([])

const maxServiceCount = computed(() => Math.max(1, ...servicesData.value.map((item) => item.count)))
const maxRevenue = computed(() => Math.max(1, ...revenueData.value.map((item) => Number(item.total))))

async function loadAnalytics() {
  error.value = ''

  const rangeError = validateDateRange(dateFrom.value, dateTo.value)
  if (rangeError) {
    error.value = rangeError
    toastStore.push({ type: 'error', title: 'Некорректный период', message: rangeError })
    return
  }

  loading.value = true

  try {
    const [summaryRes, servicesRes, visitsRes, revenueRes] = await Promise.all([
      analyticsApi.getSummary({ dateFrom: dateFrom.value, dateTo: dateTo.value }),
      analyticsApi.getServices({ dateFrom: dateFrom.value, dateTo: dateTo.value }),
      analyticsApi.getVisits({ dateFrom: dateFrom.value, dateTo: dateTo.value }),
      analyticsApi.getRevenue({ dateFrom: dateFrom.value, dateTo: dateTo.value }),
    ])

    summary.value = summaryRes
    servicesData.value = servicesRes.items
    repeatClients.value = visitsRes.repeat_clients
    revenueData.value = revenueRes.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить аналитику'
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)
</script>
