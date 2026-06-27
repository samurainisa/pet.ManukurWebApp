<template>
  <article class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
    <header class="border-b border-slate-100 pb-3">
      <h3 class="font-semibold text-slate-800">{{ client.full_name }}</h3>
      <p class="mt-0.5 text-xs text-slate-400">ID: {{ client.id }}</p>
    </header>

    <dl class="mt-3 space-y-3 text-sm text-slate-700">
      <div class="flex items-center justify-between gap-3">
        <dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-500">Телефон</dt>
        <dd class="min-w-0 break-all text-right">{{ client.phone }}</dd>
      </div>
      <div class="flex items-center justify-between gap-3 border-t border-slate-100 pt-3">
        <dt class="shrink-0 text-xs font-semibold uppercase tracking-wide text-slate-500">Оплаты</dt>
        <dd class="min-w-0 flex justify-end">
          <MoneyBadge :value="client.total_paid || '0'" />
        </dd>
      </div>
    </dl>

    <div class="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row">
      <button class="btn-muted w-full sm:flex-1" type="button" @click="emit('edit', client)">Редактировать</button>
      <RouterLink class="btn-muted w-full text-center sm:flex-1" :to="`/clients/${client.id}`">История</RouterLink>
    </div>
  </article>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

import MoneyBadge from './MoneyBadge.vue'
import type { Client } from '@/entities/client'

defineProps<{
  client: Client
}>()

const emit = defineEmits<{
  edit: [client: Client]
}>()
</script>
