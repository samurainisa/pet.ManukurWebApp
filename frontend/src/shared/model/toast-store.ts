import { defineStore } from 'pinia'
import { ref } from 'vue'

import type { ToastType } from '@/shared/types/domain'

export interface ToastItem {
  id: number
  title?: string
  message: string
  type: ToastType
}

interface PushToastPayload {
  title?: string
  message: string
  type?: ToastType
  durationMs?: number
}

export const useToastStore = defineStore('toast', () => {
  const items = ref<ToastItem[]>([])
  let idCounter = 0

  function remove(id: number): void {
    items.value = items.value.filter((item) => item.id !== id)
  }

  function push(payload: PushToastPayload): number {
    const id = ++idCounter
    const item: ToastItem = {
      id,
      title: payload.title,
      message: payload.message,
      type: payload.type ?? 'info',
    }

    items.value = [...items.value, item]

    const durationMs = payload.durationMs ?? 5000
    if (durationMs > 0) {
      window.setTimeout(() => remove(id), durationMs)
    }

    return id
  }

  return {
    items,
    push,
    remove,
  }
})
