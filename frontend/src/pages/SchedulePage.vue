<template>
  <section class="space-y-6">
    <PageHeader title="Расписание" subtitle="Записи по дням и неделям, ручное создание, перенос и отмена" />

    <div class="card flex flex-wrap items-end gap-3">
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Дата</label>
        <input v-model="selectedDate" class="input" type="date" @change="loadCalendar" />
      </div>

      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Режим</label>
        <select v-model="viewMode" class="input" @change="loadCalendar">
          <option value="day">День</option>
          <option value="week">Неделя</option>
        </select>
      </div>

      <button class="btn-muted" type="button" @click="loadCalendar">Обновить</button>
    </div>

    <div class="grid gap-4 xl:grid-cols-[2fr,1fr]">
      <div class="space-y-4">
        <LoadingBlock v-if="loading" text="Загружаю расписание..." />
        <ErrorBlock v-else-if="error" :message="error" />

        <template v-else>
          <article v-if="viewMode === 'day'" class="card">
            <h2 class="text-lg font-semibold text-slate-800">День {{ selectedDate }}</h2>

            <EmptyState
              v-if="dayAppointments.length === 0"
              class="mt-4"
              title="На выбранный день записей нет"
              description="Добавьте новую запись через форму справа."
            />

            <div v-else class="mt-4 space-y-3">
              <article
                v-for="appointment in dayAppointments"
                :key="appointment.id"
                class="rounded-2xl border border-slate-200 px-4 py-3"
              >
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p class="font-semibold text-slate-800">{{ appointment.client_name }}</p>
                    <p class="text-sm text-slate-500">{{ appointment.service_name }}</p>
                  </div>
                  <div class="text-right">
                    <StatusBadge :status="appointment.status" />
                    <p class="mt-1 text-xs text-slate-400">{{ formatDateTime(appointment.start_datetime) }}</p>
                  </div>
                </div>

                <div class="mt-3 flex flex-wrap gap-2">
                  <RouterLink class="btn-muted" :to="`/appointments/${appointment.id}`">Открыть</RouterLink>
                  <button class="btn-muted" type="button" @click="onReschedule(appointment.id, appointment.planned_duration_min)">
                    Перенести
                  </button>
                  <button class="btn-muted" type="button" @click="onCancel(appointment.id)">Отменить</button>
                  <button class="btn-muted" type="button" @click="onNoShow(appointment.id)">Неявка</button>
                </div>
              </article>
            </div>
          </article>

          <article v-else class="space-y-3">
            <article v-for="day in weekDays" :key="day.date" class="card">
              <h3 class="text-base font-semibold text-slate-800">{{ day.date }}</h3>
              <EmptyState v-if="day.appointments.length === 0" class="mt-3" title="Пусто" description="Записей нет" />
              <div v-else class="mt-3 grid gap-2 sm:grid-cols-2">
                <div
                  v-for="appointment in day.appointments"
                  :key="appointment.id"
                  class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2"
                >
                  <p class="font-semibold text-slate-700">{{ appointment.client_name }}</p>
                  <p class="text-sm text-slate-500">{{ appointment.service_name }}</p>
                  <p class="text-xs text-slate-400">{{ formatDateTime(appointment.start_datetime) }}</p>
                </div>
              </div>
            </article>
          </article>
        </template>
      </div>

      <article class="card h-fit">
        <h2 class="text-lg font-semibold text-slate-800">Новая запись</h2>

        <form class="mt-4 space-y-3" @submit.prevent="onCreateAppointment">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Клиент</label>
            <select v-model.number="form.client" class="input" required>
              <option disabled value="0">Выберите клиента</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.full_name }} ({{ client.phone }})
              </option>
            </select>
          </div>

          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Услуга</label>
            <select v-model.number="form.service" class="input" required @change="onServiceChange">
              <option disabled value="0">Выберите услугу</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Дата</label>
              <input v-model="form.date" class="input" type="date" required />
            </div>
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Время</label>
              <input v-model="form.time" class="input" type="time" required />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Минуты</label>
              <input v-model.number="form.planned_duration_min" class="input" type="number" min="5" required />
            </div>
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Цена</label>
              <input v-model.number="form.planned_price" class="input" type="number" min="0" step="0.01" required />
            </div>
          </div>

          <textarea v-model="form.comment_client" class="input min-h-20" placeholder="Комментарий клиента" />
          <textarea v-model="form.comment_master" class="input min-h-20" placeholder="Комментарий мастера" />

          <label class="flex items-center gap-2 text-sm text-slate-600">
            <input v-model="form.needs_removal" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Нужно снятие
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-600">
            <input v-model="form.needs_strengthening" type="checkbox" class="h-4 w-4 rounded border-slate-300" />
            Нужно укрепление
          </label>

          <textarea v-model="form.design_notes" class="input min-h-20" placeholder="Заметки по дизайну" />

          <p v-if="formError" class="text-sm text-rose-600">{{ formError }}</p>
          <p v-if="formSuccess" class="text-sm text-emerald-600">{{ formSuccess }}</p>

          <button class="btn-primary w-full" type="submit" :disabled="submitting">
            {{ submitting ? 'Сохранение...' : 'Создать запись' }}
          </button>
        </form>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { clientApi } from '@/entities/client'
import { appointmentApi } from '@/entities/appointment'
import type { Appointment } from '@/entities/appointment'
import { serviceApi } from '@/entities/service'
import type { Service } from '@/entities/service'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatusBadge from '@/shared/ui/StatusBadge.vue'
import { formatDateTime, toDateInputValue } from '@/shared/lib/format'
import { toNullableText, validatePositiveNumber } from '@/shared/lib/validation'

const toastStore = useToastStore()

const loading = ref(true)
const error = ref('')

const selectedDate = ref(toDateInputValue(new Date()))
const viewMode = ref<'day' | 'week'>('day')

const dayAppointments = ref<Appointment[]>([])
const weekDays = ref<{ date: string; appointments: Appointment[] }[]>([])

const clients = ref<{ id: number; full_name: string; phone: string }[]>([])
const services = ref<Service[]>([])

const submitting = ref(false)
const formError = ref('')
const formSuccess = ref('')

const form = reactive({
  client: 0,
  service: 0,
  date: toDateInputValue(new Date()),
  time: '10:00',
  planned_duration_min: 60,
  planned_price: 1500,
  comment_client: '',
  comment_master: '',
  needs_removal: false,
  needs_strengthening: false,
  design_notes: '',
})

function onServiceChange() {
  const service = services.value.find((item) => item.id === form.service)
  if (!service) {
    return
  }

  form.planned_duration_min = service.base_duration_min
  form.planned_price = Number(service.base_price)
}

async function loadReferenceData() {
  const [clientsResponse, servicesResponse] = await Promise.all([
    clientApi.getList({ page: 1 }),
    serviceApi.getList({ isActive: true }),
  ])
  clients.value = clientsResponse.results
  services.value = servicesResponse.results
}

async function loadCalendar() {
  loading.value = true
  error.value = ''

  try {
    if (viewMode.value === 'day') {
      const response = await appointmentApi.getCalendarDay(selectedDate.value)
      dayAppointments.value = response.appointments
    } else {
      const response = await appointmentApi.getCalendarWeek(selectedDate.value)
      weekDays.value = response.days
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить расписание.'
  } finally {
    loading.value = false
  }
}

async function onCreateAppointment() {
  formError.value = ''
  formSuccess.value = ''

  if (form.client <= 0) {
    formError.value = 'Выберите клиента.'
    return
  }
  if (form.service <= 0) {
    formError.value = 'Выберите услугу.'
    return
  }
  if (!form.date || !form.time) {
    formError.value = 'Укажите дату и время записи.'
    return
  }

  const durationError = validatePositiveNumber(form.planned_duration_min, 'Длительность', 5)
  if (durationError) {
    formError.value = durationError
    return
  }
  if (!Number.isInteger(form.planned_duration_min)) {
    formError.value = 'Длительность должна быть целым числом.'
    return
  }

  const priceError = validatePositiveNumber(form.planned_price, 'Цена', 0)
  if (priceError) {
    formError.value = priceError
    return
  }

  const start = new Date(`${form.date}T${form.time}`)
  if (Number.isNaN(start.getTime())) {
    formError.value = 'Некорректная дата или время записи.'
    return
  }

  submitting.value = true

  try {
    await appointmentApi.create({
      client: form.client,
      service: form.service,
      start_datetime: start.toISOString(),
      planned_duration_min: form.planned_duration_min,
      planned_price: String(form.planned_price),
      comment_client: toNullableText(form.comment_client),
      comment_master: toNullableText(form.comment_master),
      needs_removal: form.needs_removal,
      needs_strengthening: form.needs_strengthening,
      design_notes: toNullableText(form.design_notes),
    })

    formSuccess.value = 'Запись создана.'
    await loadCalendar()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : 'Не удалось создать запись.'
  } finally {
    submitting.value = false
  }
}

async function onCancel(id: number) {
  const reason = window.prompt('Причина отмены (необязательно):', '') ?? ''
  try {
    await appointmentApi.cancel(id, { reason })
    await loadCalendar()
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

async function onNoShow(id: number) {
  try {
    await appointmentApi.markNoShow(id)
    await loadCalendar()
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

async function onReschedule(id: number, duration: number) {
  if (!Number.isFinite(duration) || duration < 5) {
    toastStore.push({
      type: 'error',
      title: 'Некорректные данные',
      message: 'Для переноса длительность записи должна быть не меньше 5 минут.',
    })
    return
  }

  const raw = window.prompt('Новая дата и время в формате YYYY-MM-DDTHH:mm', `${selectedDate.value}T11:00`)
  if (!raw) {
    return
  }

  const parsed = new Date(raw)
  if (Number.isNaN(parsed.getTime())) {
    toastStore.push({
      type: 'error',
      title: 'Некорректный ввод',
      message: 'Проверьте введенное значение.',
    })
    return
  }

  try {
    await appointmentApi.reschedule(id, {
      start_datetime: parsed.toISOString(),
      planned_duration_min: duration,
    })
    await loadCalendar()
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

onMounted(async () => {
  try {
    await loadReferenceData()
  } catch {
    // noop
  }
  await loadCalendar()
})
</script>
