<template>
  <section class="space-y-6">
    <PageHeader title="Мои визиты" subtitle="История и ближайшие записи на услуги." />

    <LoadingBlock v-if="loading" text="Загружаю ваши записи..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <article v-else class="card">
      <EmptyState
        v-if="appointments.length === 0"
        title="Записей пока нет"
        description="Оформите первую запись через раздел «Записаться»."
      />

      <div v-else class="space-y-3">
        <div
          v-for="appointment in appointments"
          :key="appointment.id"
          class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <p class="text-base font-semibold text-slate-900">{{ appointment.service_name }}</p>
            <StatusBadge :status="appointment.status" />
          </div>

          <p class="mt-1 text-sm text-slate-500">
            {{ formatDateTime(appointment.start_datetime) }} · {{ appointment.planned_duration_min }} мин
          </p>
          <p class="mt-2 text-sm text-slate-700">Стоимость: {{ formatMoney(appointment.planned_price) }}</p>
          <p v-if="appointment.comment_client" class="mt-2 text-sm text-slate-600">
            Комментарий: {{ appointment.comment_client }}
          </p>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { clientPortalApi } from '@/entities/client-portal'
import type { Appointment } from '@/entities/appointment'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatusBadge from '@/shared/ui/StatusBadge.vue'
import { formatDateTime, formatMoney } from '@/shared/lib/format'

const loading = ref(true)
const error = ref('')
const appointments = ref<Appointment[]>([])

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const response = await clientPortalApi.getBookings()
    appointments.value = response.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить записи.'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
