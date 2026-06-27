<template>
  <div class="pointer-events-none fixed right-4 top-4 z-[100] flex w-[min(92vw,400px)] flex-col gap-2">
    <transition-group name="toast" tag="div">
      <article
        v-for="toast in toastStore.items"
        :key="toast.id"
        class="pointer-events-auto rounded-2xl border px-4 py-3 shadow-lg backdrop-blur"
        :class="toastClass(toast.type)"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <p v-if="toast.title" class="text-sm font-semibold">{{ toast.title }}</p>
            <p class="text-sm whitespace-pre-line">{{ toast.message }}</p>
          </div>
          <button class="btn-muted !px-2 !py-1 text-xs" type="button" @click="toastStore.remove(toast.id)">
            x
          </button>
        </div>
      </article>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToastStore } from '@/shared/model/toast-store'
import type { ToastType } from '@/shared/types/domain'

const toastStore = useToastStore()

function toastClass(type: ToastType) {
  if (type === 'success') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-900'
  }
  if (type === 'error') {
    return 'border-rose-200 bg-rose-50 text-rose-900'
  }
  return 'border-slate-200 bg-white text-slate-800'
}
</script>
