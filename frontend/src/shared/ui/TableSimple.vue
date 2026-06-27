<template>
  <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
    <table class="min-w-full divide-y divide-slate-100 text-sm">
      <thead class="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th v-for="column in columns" :key="column" class="px-4 py-3">{{ column }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 text-slate-700">
        <slot />
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  columns: string[]
}>()
</script>
