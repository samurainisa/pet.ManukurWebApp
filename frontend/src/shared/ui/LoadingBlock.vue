<template>
  <div class="card flex items-center gap-3 text-sm text-slate-500">
    <span class="inline-block h-2.5 w-2.5 animate-pulse rounded-full bg-[var(--primary)]" />
    {{ text }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text?: string
}>()
</script>