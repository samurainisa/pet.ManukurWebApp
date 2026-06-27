<template>
  <section class="space-y-6">
    <PageHeader title="Клиенты" subtitle="База клиентов с поиском, историей и заметками" />

    <div class="grid gap-4 lg:grid-cols-2 xl:grid-cols-[2fr,1fr]">
      <div class="space-y-4">
        <div class="card flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
          <input
            v-model="search"
            class="input w-full sm:max-w-md"
            type="text"
            placeholder="Поиск по имени или телефону"
            @input="onSearch"
          />
          <button class="btn-muted" type="button" @click="loadClients">Обновить</button>
        </div>

        <LoadingBlock v-if="loading" text="Загружаю список клиентов..." />
        <ErrorBlock v-else-if="error" :message="error" />

        <template v-else>
          <EmptyState
            v-if="clients.length === 0"
            title="Список клиентов пуст"
            description="Добавьте первого клиента через форму справа."
          />

          <div v-else class="space-y-3">
            <ClientListCard v-for="item in clients" :key="item.id" :client="item" @edit="startEdit" />
          </div>

          <div class="flex flex-col gap-3 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
            <p>Всего: {{ count }}</p>
            <div class="flex flex-wrap gap-2">
              <button class="btn-muted" type="button" :disabled="page <= 1" @click="changePage(page - 1)">
                Назад
              </button>
              <button class="btn-muted" type="button" :disabled="!hasNext" @click="changePage(page + 1)">
                Вперед
              </button>
            </div>
          </div>
        </template>
      </div>

      <article class="card h-fit">
        <h2 class="text-lg font-semibold text-slate-800">
          {{ editId ? 'Редактирование клиента' : 'Новый клиент' }}
        </h2>

        <form class="mt-4 space-y-3" @submit.prevent="onSubmit">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">ФИО</label>
            <input v-model="form.full_name" class="input" type="text" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Телефон</label>
            <input v-model="form.phone" class="input" type="text" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
            <input v-model="form.email" class="input" type="email" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Заметки</label>
            <textarea v-model="form.notes" class="input min-h-24 resize-y" />
          </div>

          <p v-if="formError" class="text-sm text-rose-600">{{ formError }}</p>
          <p v-if="formSuccess" class="text-sm text-emerald-600">{{ formSuccess }}</p>

          <div class="flex gap-2">
            <button class="btn-primary flex-1" type="submit" :disabled="submitting">
              {{ submitting ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button v-if="editId" class="btn-muted" type="button" @click="resetForm">Сброс</button>
          </div>
        </form>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { onMounted, reactive, ref } from 'vue'

import { clientApi, useClientStore, type Client } from '@/entities/client'
import ClientListCard from '@/shared/ui/ClientListCard.vue'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import {
  normalizeSpaces,
  toNullableText,
  validateOptionalEmail,
  validatePhone,
  validateRequiredText,
} from '@/shared/lib/validation'

const clientStore = useClientStore()
const { items: clients, loading, error, search, page, hasNext, count } = storeToRefs(clientStore)

const editId = ref<number | null>(null)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref('')

const form = reactive({
  full_name: '',
  phone: '',
  email: '',
  notes: '',
})

let searchTimer: number | null = null

function resetForm() {
  editId.value = null
  form.full_name = ''
  form.phone = ''
  form.email = ''
  form.notes = ''
  formError.value = ''
  formSuccess.value = ''
}

function startEdit(client: Client) {
  editId.value = client.id
  form.full_name = client.full_name
  form.phone = client.phone
  form.email = client.email || ''
  form.notes = client.notes || ''
  formError.value = ''
  formSuccess.value = ''
}

async function loadClients() {
  await clientStore.fetchList()
}

function onSearch() {
  if (searchTimer) {
    window.clearTimeout(searchTimer)
  }
  searchTimer = window.setTimeout(() => {
    clientStore.setPage(1)
    clientStore.fetchList({ search: search.value, page: 1 })
  }, 250)
}

function changePage(nextPage: number) {
  clientStore.fetchList({ page: nextPage })
}

async function onSubmit() {
  formError.value = ''
  formSuccess.value = ''

  const fullNameError = validateRequiredText(form.full_name, 'ФИО', 2)
  if (fullNameError) {
    formError.value = fullNameError
    return
  }

  const phoneError = validatePhone(form.phone)
  if (phoneError) {
    formError.value = phoneError
    return
  }

  const emailError = validateOptionalEmail(form.email)
  if (emailError) {
    formError.value = emailError
    return
  }

  submitting.value = true

  try {
    const payload = {
      full_name: normalizeSpaces(form.full_name),
      phone: normalizeSpaces(form.phone),
      email: form.email.trim() || null,
      notes: toNullableText(form.notes),
    }

    if (editId.value) {
      await clientApi.update(editId.value, payload)
      formSuccess.value = 'Клиент обновлен'
    } else {
      await clientApi.create(payload)
      formSuccess.value = 'Клиент добавлен'
      resetForm()
    }

    await loadClients()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : 'Не удалось сохранить клиента'
  } finally {
    submitting.value = false
  }
}

onMounted(loadClients)
</script>
