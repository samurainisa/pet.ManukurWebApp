<template>
  <section class="space-y-6">
    <PageHeader
      title="Запись на услугу"
      subtitle="Выберите услугу, дату и свободное время для записи."
    />

    <LoadingBlock v-if="loadingServices" text="Загружаю услуги..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <div v-else class="grid gap-4 lg:grid-cols-[1.5fr,1fr]">
      <article class="card space-y-4">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
            Услуга
          </label>
          <select v-model.number="form.service_id" class="input" required @change="loadSlots">
            <option disabled value="0">Выберите услугу</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }} — {{ formatMoney(service.base_price) }} · {{ service.base_duration_min }} мин
            </option>
          </select>
        </div>

        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Дата</label>
          <input v-model="form.date" class="input max-w-56" type="date" required @change="loadSlots" />
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-500">
            Свободное время
          </label>
          <LoadingBlock v-if="loadingSlots" text="Подбираю слоты..." />
          <EmptyState
            v-else-if="slots.length === 0"
            title="Свободных слотов нет"
            description="Попробуйте выбрать другую дату."
          />
          <div v-else class="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
            <button
              v-for="slot in slots"
              :key="slot"
              type="button"
              class="btn-muted h-11"
              :class="selectedSlot === slot ? '!border-sky-500 !bg-sky-100 !text-sky-700' : ''"
              @click="selectedSlot = slot"
            >
              {{ slotTime(slot) }}
            </button>
          </div>
        </div>
      </article>

      <article class="card space-y-4">
        <h2 class="text-lg font-semibold text-slate-900">Подтверждение записи</h2>

        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
          <p><span class="font-medium text-slate-900">Услуга:</span> {{ selectedService?.name || 'Не выбрана' }}</p>
          <p class="mt-1"><span class="font-medium text-slate-900">Дата:</span> {{ form.date || 'Не выбрана' }}</p>
          <p class="mt-1"><span class="font-medium text-slate-900">Время:</span> {{ selectedSlotLabel }}</p>
        </div>

        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
            Комментарий
          </label>
          <textarea
            v-model="form.comment"
            class="input min-h-24"
            placeholder="Пожелания к визиту"
          />
        </div>

        <p v-if="submitError" class="text-sm text-rose-600">{{ submitError }}</p>

        <button class="btn-primary w-full py-3" type="button" :disabled="submitting || !selectedSlot" @click="onSubmit">
          {{ submitting ? 'Отправка...' : 'Записаться' }}
        </button>

        <RouterLink class="btn-muted w-full" to="/client/notifications">Открыть уведомления</RouterLink>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { clientPortalApi } from '@/entities/client-portal'
import { serviceApi } from '@/entities/service'
import type { Service } from '@/entities/service'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import { formatMoney, toDateInputValue } from '@/shared/lib/format'
import { toNullableText } from '@/shared/lib/validation'

const toastStore = useToastStore()

const loadingServices = ref(true)
const loadingSlots = ref(false)
const submitting = ref(false)
const error = ref('')
const submitError = ref('')

const services = ref<Service[]>([])
const slots = ref<string[]>([])
const selectedSlot = ref('')

const form = reactive({
  service_id: 0,
  date: toDateInputValue(new Date(Date.now() + 24 * 60 * 60 * 1000)),
  comment: '',
})

const selectedService = computed(() => services.value.find((item) => item.id === form.service_id))
const selectedSlotLabel = computed(() => (selectedSlot.value ? slotTime(selectedSlot.value) : 'Не выбрано'))

function slotTime(value: string) {
  return new Date(value).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

async function loadServices() {
  loadingServices.value = true
  error.value = ''

  try {
    const response = await serviceApi.getPublicList()
    services.value = response.results
    if (response.results.length > 0) {
      form.service_id = response.results[0].id
      await loadSlots()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить услуги.'
  } finally {
    loadingServices.value = false
  }
}

async function loadSlots() {
  if (!form.service_id || !form.date) {
    slots.value = []
    selectedSlot.value = ''
    return
  }

  loadingSlots.value = true
  submitError.value = ''
  selectedSlot.value = ''

  try {
    const response = await clientPortalApi.getAvailableSlots(form.service_id, form.date)
    slots.value = response.slots
  } catch (err) {
    slots.value = []
    submitError.value = err instanceof Error ? err.message : 'Не удалось загрузить слоты.'
  } finally {
    loadingSlots.value = false
  }
}

async function onSubmit() {
  if (form.service_id <= 0) {
    submitError.value = 'Выберите услугу.'
    return
  }
  if (!form.date) {
    submitError.value = 'Выберите дату.'
    return
  }
  if (!selectedSlot.value) {
    submitError.value = 'Выберите свободное время.'
    return
  }

  const date = selectedSlot.value.slice(0, 10)
  const time = selectedSlot.value.slice(11, 16)
  if (!date || !time || time.length !== 5) {
    submitError.value = 'Некорректное время слота. Выберите слот заново.'
    return
  }

  submitting.value = true
  submitError.value = ''
  try {
    await clientPortalApi.createBooking({
      service_id: form.service_id,
      date,
      time,
      comment: toNullableText(form.comment) ?? '',
    })
    form.comment = ''
    selectedSlot.value = ''
    await loadSlots()
    toastStore.push({
      type: 'success',
      title: 'Запись создана',
      message: 'Визит добавлен в ваш список записей.',
    })
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : 'Не удалось создать запись.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadServices)
</script>
