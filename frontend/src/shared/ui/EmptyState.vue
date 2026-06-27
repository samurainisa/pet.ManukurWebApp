<template>
  <div class="card border border-dashed border-slate-200 text-center text-sm text-slate-500">
    <p class="font-medium">{{ title }}</p>
    <p v-if="description" class="mt-1 text-xs text-slate-400">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>