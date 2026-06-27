<template>
  <section class="space-y-6">
    <PageHeader title="История клиента" subtitle="Просмотр визитов и оплат по клиенту" />

    <LoadingBlock v-if="loading" text="Загружаю карточку клиента..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <template v-else-if="history">
      <article class="card">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-slate-800">{{ history.client.full_name }}</h2>
            <p class="text-sm text-slate-500">{{ history.client.phone }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-slate-500">Общая сумма оплат</p>
            <p class="text-lg font-bold text-slate-800">{{ formatMoney(history.total_paid) }}</p>
          </div>
        </div>

        <p v-if="history.client.notes" class="mt-4 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">
          {{ history.client.notes }}
        </p>
      </article>

      <article class="card">
        <h3 class="text-lg font-semibold text-slate-800">История визитов</h3>

        <EmptyState
          v-if="history.history.length === 0"
          title="Визитов пока нет"
          description="После первого завершенного визита история появится здесь."
          class="mt-4"
        />

        <TableSimple v-else class="mt-4" :columns="['Дата', 'Услуга', 'Статус', 'Оплата', 'Комментарий']">
          <tr v-for="visit in history.history" :key="visit.id" class="hover:bg-slate-50">
            <td class="px-4 py-3">{{ formatDateTime(visit.start_datetime) }}</td>
            <td class="px-4 py-3">{{ visit.service_name }}</td>
            <td class="px-4 py-3"><StatusBadge :status="visit.status" /></td>
            <td class="px-4 py-3">
              <div class="flex flex-col gap-1">
                <MoneyBadge :value="visit.payment_amount || '0'" />
                <StatusBadge :status="visit.payment_status" />
              </div>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ visit.comment_master || '—' }}</td>
          </tr>
        </TableSimple>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { clientApi } from '@/entities/client'
import type { ClientHistoryResponse } from '@/entities/client'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import MoneyBadge from '@/shared/ui/MoneyBadge.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatusBadge from '@/shared/ui/StatusBadge.vue'
import TableSimple from '@/shared/ui/TableSimple.vue'
import { formatDateTime, formatMoney } from '@/shared/lib/format'

const route = useRoute()

const loading = ref(true)
const error = ref('')
const history = ref<ClientHistoryResponse | null>(null)

async function loadHistory() {
  loading.value = true
  error.value = ''

  try {
    const id = Number(route.params.id)
    history.value = await clientApi.getHistory(id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить историю клиента'
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>