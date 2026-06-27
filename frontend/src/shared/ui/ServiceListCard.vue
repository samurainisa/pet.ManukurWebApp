<template>
  <article class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
    <header class="border-b border-slate-100 pb-3">
      <h3 class="font-semibold text-slate-800">{{ service.name }}</h3>
      <p class="mt-0.5 text-xs text-slate-400">{{ service.description || 'Без описания' }}</p>
    </header>

    <dl class="mt-3 space-y-3 text-sm text-slate-700">
      <div class="flex items-center justify-between gap-3">
        <dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-500">Длительность</dt>
        <dd class="min-w-0 text-right">{{ service.base_duration_min }} мин</dd>
      </div>
      <div class="flex items-center justify-between gap-3 border-t border-slate-100 pt-3">
        <dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-500">Цена</dt>
        <dd class="min-w-0 flex justify-end">
          <MoneyBadge :value="service.base_price" />
        </dd>
      </div>
      <div class="flex items-center justify-between gap-3 border-t border-slate-100 pt-3">
        <dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-500">Статус</dt>
        <dd class="min-w-0 flex justify-end">
          <span
            class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="service.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'"
          >
            {{ service.is_active ? 'Активна' : 'Отключена' }}
          </span>
        </dd>
      </div>
    </dl>

    <div class="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row">
      <button class="btn-muted w-full sm:flex-1" type="button" @click="emit('edit', service)">Редактировать</button>
      <button
        class="btn-danger w-full sm:flex-1"
        type="button"
        :disabled="deleting"
        @click="emit('delete', service)"
      >
        {{ deleting ? 'Удаление...' : 'Удалить' }}
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import MoneyBadge from './MoneyBadge.vue'
import type { Service } from '@/entities/service'

defineProps<{
  service: Service
  deleting?: boolean
}>()

const emit = defineEmits<{
  edit: [service: Service]
  delete: [service: Service]
}>()
</script>
