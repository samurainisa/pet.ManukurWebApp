<template>
  <div class="mb-4 md:mb-6">
    <h1 class="text-xl font-bold text-slate-800 md:text-2xl">{{ title }}</h1>
    <p v-if="subtitle" class="mt-1 text-sm text-slate-500">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>