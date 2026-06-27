<template>
  <div class="card border border-rose-100 bg-rose-50 text-sm text-rose-700">
    <p class="font-semibold">Ошибка</p>
    <p class="mt-1">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>