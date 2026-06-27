import { defineStore } from 'pinia'
import { ref } from 'vue'

import { clientApi } from '../api/ClientApi'
import type { Client, ClientListParams } from '../model/types'

export const useClientStore = defineStore('client', () => {
  const items = ref<Client[]>([])
  const count = ref(0)
  const hasNext = ref(false)
  const loading = ref(false)
  const error = ref('')
  const search = ref('')
  const page = ref(1)

  async function fetchList(params: ClientListParams = {}): Promise<void> {
    loading.value = true
    error.value = ''

    const nextSearch = params.search ?? search.value
    const nextPage = params.page ?? page.value

    try {
      const response = await clientApi.getList({ search: nextSearch, page: nextPage })
      items.value = response.results
      count.value = response.count
      hasNext.value = Boolean(response.next)
      search.value = nextSearch
      page.value = nextPage
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Не удалось загрузить клиентов'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSearch(value: string): void {
    search.value = value
  }

  function setPage(value: number): void {
    page.value = value
  }

  return {
    items,
    count,
    hasNext,
    loading,
    error,
    search,
    page,
    fetchList,
    setSearch,
    setPage,
  }
})
