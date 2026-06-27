<template>
  <section class="space-y-6">
    <PageHeader title="Уведомления" subtitle="Напоминания и статусы ваших визитов." />

    <LoadingBlock v-if="loading" text="Загружаю уведомления..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <article v-else class="card">
      <EmptyState
        v-if="items.length === 0"
        title="Уведомлений нет"
        description="Когда появятся новые статусы визитов, они отобразятся здесь."
      />

      <div v-else class="space-y-3">
        <div
          v-for="item in items"
          :key="`${item.appointment_id}-${item.title}-${item.start_datetime ?? 'none'}`"
          class="rounded-2xl border p-4"
          :class="colorClass(item.type)"
        >
          <div class="flex flex-wrap items-start justify-between gap-2">
            <p class="text-base font-semibold">{{ item.title }}</p>
            <p v-if="item.start_datetime" class="text-xs opacity-80">
              {{ formatDateTime(item.start_datetime) }}
            </p>
          </div>
          <p class="mt-2 text-sm">{{ item.message }}</p>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { clientPortalApi } from '@/entities/client-portal'
import type { ClientNotificationItem } from '@/entities/client-portal/model/types'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import { formatDateTime } from '@/shared/lib/format'

const loading = ref(true)
const error = ref('')
const items = ref<ClientNotificationItem[]>([])

function colorClass(type: ClientNotificationItem['type']) {
  if (type === 'success') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-900'
  }
  if (type === 'warning') {
    return 'border-amber-200 bg-amber-50 text-amber-900'
  }
  return 'border-sky-200 bg-sky-50 text-sky-900'
}

async function loadData() {
  loading.value = true
  error.value = ''

  try {
    const response = await clientPortalApi.getNotifications()
    items.value = response.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить уведомления.'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
