<template>
  <article class="card">
    <p class="text-sm text-slate-500">{{ label }}</p>
    <p class="mt-3 text-2xl font-bold text-slate-900">{{ value }}</p>
    <p v-if="hint" class="mt-2 text-xs text-slate-400">{{ hint }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint?: string
}>()
</script>