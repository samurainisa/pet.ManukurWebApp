<template>
  <span :class="badgeClass" class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AppointmentStatus, PaymentStatus } from '@/shared/types/domain'

const props = defineProps<{
  status: AppointmentStatus | PaymentStatus | null
}>()

const statusMap: Record<string, { label: string; className: string }> = {
  created: { label: 'Создана', className: 'bg-slate-100 text-slate-700' },
  confirmed: { label: 'Подтверждена', className: 'bg-cyan-100 text-cyan-700' },
  completed: { label: 'Выполнена', className: 'bg-emerald-100 text-emerald-700' },
  cancelled: { label: 'Отменена', className: 'bg-rose-100 text-rose-700' },
  rescheduled: { label: 'Перенесена', className: 'bg-amber-100 text-amber-700' },
  no_show: { label: 'Неявка', className: 'bg-orange-100 text-orange-700' },
  paid: { label: 'Оплачено', className: 'bg-emerald-100 text-emerald-700' },
  unpaid: { label: 'Не оплачено', className: 'bg-slate-100 text-slate-700' },
  partial: { label: 'Частично', className: 'bg-amber-100 text-amber-700' },
}

const badge = computed(() => {
  if (!props.status) {
    return { label: 'Нет данных', className: 'bg-slate-100 text-slate-600' }
  }
  return statusMap[props.status] ?? { label: props.status, className: 'bg-slate-100 text-slate-700' }
})

const label = computed(() => badge.value.label)
const badgeClass = computed(() => badge.value.className)
</script>