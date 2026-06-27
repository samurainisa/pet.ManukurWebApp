<template>
  <main class="mx-auto flex min-h-screen w-full max-w-xl items-center justify-center px-4 py-10">
    <section class="w-full rounded-3xl bg-white p-8 text-center shadow-[0_18px_55px_rgba(20,40,45,0.12)]">
      <p class="text-xs uppercase tracking-[0.2em] text-emerald-500">Успешно</p>
      <h1 class="mt-2 text-2xl font-bold text-slate-900">Запись оформлена</h1>
      <p class="mt-2 text-sm text-slate-500">
        Спасибо! Заявка уже в расписании мастера.
        Номер записи: <span class="font-semibold text-slate-700">{{ bookingId }}</span>
      </p>

      <div class="mt-6 flex flex-wrap justify-center gap-2">
        <RouterLink class="btn-muted" to="/book">Сделать ещё запись</RouterLink>
        <RouterLink class="btn-primary" to="/login">Вход для мастера</RouterLink>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const bookingId = computed(() => String(route.query.id || '—'))
</script>
