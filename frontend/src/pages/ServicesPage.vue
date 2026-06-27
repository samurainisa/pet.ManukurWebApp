<template>
  <section class="space-y-6">
    <PageHeader title="Услуги" subtitle="Справочник услуг с длительностью, ценой и статусом" />

    <div class="grid items-start gap-4 lg:grid-cols-2 xl:grid-cols-[2fr,1fr]">
      <div class="min-w-0 space-y-4">
        <div class="card flex items-center gap-3">
          <button class="btn-muted" type="button" @click="loadServices">Обновить</button>
        </div>

        <LoadingBlock v-if="loading" text="Загружаю услуги..." />
        <ErrorBlock v-else-if="error" :message="error" />

        <template v-else>
          <EmptyState
            v-if="services.length === 0"
            title="Справочник пуст"
            description="Добавьте первую услугу через форму справа."
          />

          <div v-else class="space-y-3">
            <ServiceListCard
              v-for="item in services"
              :key="item.id"
              :service="item"
              :deleting="deletingId === item.id"
              @edit="startEdit"
              @delete="onDelete"
            />
          </div>
        </template>
      </div>

      <article class="card h-fit">
        <h2 class="text-lg font-semibold text-slate-800">
          {{ editId ? 'Редактирование услуги' : 'Новая услуга' }}
        </h2>

        <form class="mt-4 space-y-3" @submit.prevent="onSubmit">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Название</label>
            <input v-model="form.name" class="input" type="text" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Описание</label>
            <textarea v-model="form.description" class="input min-h-20" />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Минуты</label>
              <input v-model.number="form.base_duration_min" class="input" type="number" min="5" required />
            </div>
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Цена</label>
              <input v-model.number="form.base_price" class="input" type="number" min="0" step="0.01" required />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Порядок</label>
            <input v-model.number="form.sort_order" class="input" type="number" min="0" required />
          </div>
          <label class="flex items-center gap-2 text-sm text-slate-600">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Услуга активна
          </label>

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

import { serviceApi, useServiceStore, type Service } from '@/entities/service'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import ServiceListCard from '@/shared/ui/ServiceListCard.vue'
import { normalizeSpaces, toNullableText, validatePositiveNumber, validateRequiredText } from '@/shared/lib/validation'

const toastStore = useToastStore()
const serviceStore = useServiceStore()
const { items: services, loading, error } = storeToRefs(serviceStore)

const editId = ref<number | null>(null)
const submitting = ref(false)
const deletingId = ref<number | null>(null)
const formError = ref('')
const formSuccess = ref('')

const form = reactive({
  name: '',
  description: '',
  base_duration_min: 60,
  base_price: 1500,
  is_active: true,
  sort_order: 0,
})

function resetForm() {
  editId.value = null
  form.name = ''
  form.description = ''
  form.base_duration_min = 60
  form.base_price = 1500
  form.is_active = true
  form.sort_order = 0
  formError.value = ''
  formSuccess.value = ''
}

function startEdit(service: Service) {
  editId.value = service.id
  form.name = service.name
  form.description = service.description || ''
  form.base_duration_min = service.base_duration_min
  form.base_price = Number(service.base_price)
  form.is_active = service.is_active
  form.sort_order = service.sort_order
  formError.value = ''
  formSuccess.value = ''
}

async function loadServices() {
  await serviceStore.fetchList()
}

async function onSubmit() {
  formError.value = ''
  formSuccess.value = ''

  const nameError = validateRequiredText(form.name, 'Название услуги', 2)
  if (nameError) {
    formError.value = nameError
    return
  }

  const durationError = validatePositiveNumber(form.base_duration_min, 'Длительность', 5)
  if (durationError) {
    formError.value = durationError
    return
  }
  if (!Number.isInteger(form.base_duration_min)) {
    formError.value = 'Длительность должна быть целым числом.'
    return
  }

  const priceError = validatePositiveNumber(form.base_price, 'Цена', 0)
  if (priceError) {
    formError.value = priceError
    return
  }

  const sortOrderError = validatePositiveNumber(form.sort_order, 'Порядок', 0)
  if (sortOrderError) {
    formError.value = sortOrderError
    return
  }
  if (!Number.isInteger(form.sort_order)) {
    formError.value = 'Порядок должен быть целым числом.'
    return
  }

  submitting.value = true

  try {
    const payload = {
      name: normalizeSpaces(form.name),
      description: toNullableText(form.description),
      base_duration_min: form.base_duration_min,
      base_price: String(form.base_price),
      is_active: form.is_active,
      sort_order: form.sort_order,
    }

    if (editId.value) {
      await serviceApi.update(editId.value, payload)
      formSuccess.value = 'Услуга обновлена'
    } else {
      await serviceApi.create(payload)
      formSuccess.value = 'Услуга добавлена'
      resetForm()
    }

    await loadServices()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : 'Не удалось сохранить услугу'
  } finally {
    submitting.value = false
  }
}

async function onDelete(service: Service) {
  const approved = window.confirm(`Удалить услугу «${service.name}»?`)
  if (!approved) {
    return
  }

  deletingId.value = service.id
  formError.value = ''
  formSuccess.value = ''

  try {
    await serviceApi.delete(service.id)
    if (editId.value === service.id) {
      resetForm()
    }
    await loadServices()
    toastStore.push({ type: 'success', title: 'Услуга удалена', message: 'Запись из справочника удалена.' })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Не удалось удалить услугу.'
    formError.value = message
    toastStore.push({ type: 'error', title: 'Ошибка удаления', message })
  } finally {
    deletingId.value = null
  }
}

onMounted(loadServices)
</script>
