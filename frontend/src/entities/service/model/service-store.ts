import { defineStore } from 'pinia'
import { ref } from 'vue'

import { serviceApi } from '../api/ServiceApi'
import type { Service, ServiceListParams } from '../model/types'

export const useServiceStore = defineStore('service', () => {
  const items = ref<Service[]>([])
  const loading = ref(false)
  const error = ref('')

  async function fetchList(params: ServiceListParams = {}): Promise<void> {
    loading.value = true
    error.value = ''

    try {
      const response = await serviceApi.getList(params)
      items.value = response.results
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Не удалось загрузить услуги'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    error,
    fetchList,
  }
})
