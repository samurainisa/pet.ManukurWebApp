<template>
  <span class="inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
    {{ formatted }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatMoney } from '@/shared/lib/format'

const props = defineProps<{
  value: string | number
}>()

const formatted = computed(() => formatMoney(props.value))
</script>