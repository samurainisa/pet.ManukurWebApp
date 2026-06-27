<template>
  <section class="space-y-6">
    <PageHeader title="Карточка визита" subtitle="Статус записи, результат процедуры, фото и оплата" />

    <LoadingBlock v-if="loading" text="Загружаю данные визита..." />
    <ErrorBlock v-else-if="error" :message="error" />

    <template v-else-if="appointment">
      <article class="card">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 class="text-xl font-semibold text-slate-800">{{ appointment.client_name }}</h2>
            <p class="text-sm text-slate-500">{{ appointment.service_name }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ formatDateTime(appointment.start_datetime) }}</p>
          </div>
          <div class="text-right">
            <StatusBadge :status="appointment.status" />
            <p class="mt-2 text-sm text-slate-500">Плановая цена: {{ formatMoney(appointment.planned_price) }}</p>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button
            class="btn-primary"
            type="button"
            @click="markCompleted"
            :disabled="appointment.status === 'completed' || statusSubmitting"
          >
            {{ statusSubmitting ? 'Сохранение...' : 'Отметить как выполнено' }}
          </button>
        </div>
      </article>

      <div class="grid gap-4 xl:grid-cols-2">
        <article class="card">
          <h3 class="text-lg font-semibold text-slate-800">Результат услуги</h3>

          <form class="mt-4 space-y-3" @submit.prevent="saveResult">
            <textarea
              v-model="resultForm.actual_service_summary"
              class="input min-h-20"
              placeholder="Фактическая услуга"
            />
            <textarea
              v-model="resultForm.materials_used"
              class="input min-h-20"
              placeholder="Использованные материалы"
            />
            <textarea
              v-model="resultForm.result_notes"
              class="input min-h-24"
              placeholder="Заметки по результату"
            />
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500"
                >Фактическая длительность (мин)</label
              >
              <input v-model.number="resultForm.actual_duration_min" class="input" min="1" type="number" />
            </div>

            <p v-if="resultError" class="text-sm text-rose-600">{{ resultError }}</p>
            <p v-if="resultSuccess" class="text-sm text-emerald-600">{{ resultSuccess }}</p>

            <button class="btn-primary w-full" type="submit" :disabled="resultSubmitting">
              {{ resultSubmitting ? 'Сохранение...' : 'Сохранить результат' }}
            </button>
          </form>

          <div class="mt-6">
            <h4 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Фото результата</h4>
            <input class="mt-2 block text-sm" type="file" accept="image/jpeg,image/png,image/webp" @change="onFileChange" />

            <div v-if="photoError" class="mt-2 text-sm text-rose-600">{{ photoError }}</div>
            <div class="mt-3 grid gap-2 sm:grid-cols-2">
              <div
                v-for="photo in photos"
                :key="photo.id"
                class="overflow-hidden rounded-xl border border-slate-200 bg-slate-50"
              >
                <img class="h-40 w-full object-cover" :src="resolveImage(photo.image)" alt="Результат" />
                <button class="btn-muted m-2" type="button" @click="removePhoto(photo.id)">Удалить</button>
              </div>
            </div>
            <EmptyState
              v-if="photos.length === 0"
              class="mt-3"
              title="Фото пока нет"
              description="Можно загрузить фотографии результата." />
          </div>
        </article>

        <article class="card">
          <h3 class="text-lg font-semibold text-slate-800">Оплата</h3>

          <form class="mt-4 space-y-3" @submit.prevent="savePaymentData">
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Сумма</label>
              <input v-model="paymentForm.amount" class="input" min="0" step="0.01" type="number" required />
            </div>

            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Способ</label>
              <select v-model="paymentForm.payment_method" class="input">
                <option value="cash">Наличные</option>
                <option value="transfer">Перевод</option>
                <option value="card_manual">Карта</option>
              </select>
            </div>

            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Статус</label>
              <select v-model="paymentForm.payment_status" class="input">
                <option value="unpaid">Не оплачено</option>
                <option value="paid">Оплачено</option>
                <option value="partial">Частично</option>
              </select>
            </div>

            <textarea v-model="paymentForm.comment" class="input min-h-24" placeholder="Комментарий к оплате" />

            <p v-if="paymentError" class="text-sm text-rose-600">{{ paymentError }}</p>
            <p v-if="paymentSuccess" class="text-sm text-emerald-600">{{ paymentSuccess }}</p>

            <button class="btn-primary w-full" type="submit" :disabled="paymentSubmitting">
              {{ paymentSubmitting ? 'Сохранение...' : 'Сохранить оплату' }}
            </button>
          </form>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { appointmentApi } from '@/entities/appointment'
import type { Appointment } from '@/entities/appointment'
import { paymentApi } from '@/entities/payment'
import type { Payment } from '@/entities/payment'
import { visitApi } from '@/entities/visit'
import type { VisitPhoto } from '@/entities/visit'
import { env } from '@/shared/config/env'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import StatusBadge from '@/shared/ui/StatusBadge.vue'
import { formatDateTime, formatMoney } from '@/shared/lib/format'
import { toNullableText } from '@/shared/lib/validation'

const toastStore = useToastStore()
const MEDIA_BASE = env.apiBaseUrl.replace('/api/v1', '')

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const route = useRoute()
const appointmentId = Number(route.params.id)

const loading = ref(true)
const error = ref('')
const appointment = ref<Appointment | null>(null)

const statusSubmitting = ref(false)

const resultSubmitting = ref(false)
const resultError = ref('')
const resultSuccess = ref('')

const photoError = ref('')
const photos = ref<VisitPhoto[]>([])

const paymentSubmitting = ref(false)
const paymentError = ref('')
const paymentSuccess = ref('')

const resultForm = reactive({
  actual_service_summary: '',
  materials_used: '',
  result_notes: '',
  actual_duration_min: null as number | null,
})

const paymentForm = reactive<Pick<Payment, 'amount' | 'payment_method' | 'payment_status' | 'comment'>>({
  amount: '0',
  payment_method: 'cash',
  payment_status: 'unpaid',
  comment: null,
})

function resolveImage(url: string) {
  if (url.startsWith('http')) {
    return url
  }
  return `${MEDIA_BASE}${url}`
}

async function loadPage() {
  loading.value = true
  error.value = ''

  try {
    const data = await appointmentApi.getById(appointmentId)
    appointment.value = data
    photos.value = (data.photos || []) as VisitPhoto[]

    try {
      const result = await visitApi.getResult(appointmentId)
      resultForm.actual_service_summary = result.actual_service_summary || ''
      resultForm.materials_used = result.materials_used || ''
      resultForm.result_notes = result.result_notes || ''
      resultForm.actual_duration_min = result.actual_duration_min ?? null
    } catch {
      resultForm.actual_service_summary = ''
      resultForm.materials_used = ''
      resultForm.result_notes = ''
      resultForm.actual_duration_min = null
    }

    const payment = await paymentApi.getByAppointment(appointmentId)
    paymentForm.amount = payment.amount
    paymentForm.payment_method = payment.payment_method
    paymentForm.payment_status = payment.payment_status
    paymentForm.comment = payment.comment
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось загрузить карточку визита.'
  } finally {
    loading.value = false
  }
}

async function markCompleted() {
  if (!appointment.value) {
    return
  }

  statusSubmitting.value = true
  try {
    appointment.value = await appointmentApi.update(appointment.value.id, { status: 'completed' })
    toastStore.push({ type: 'success', title: 'Статус обновлен', message: 'Визит отмечен как выполненный.' })
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  } finally {
    statusSubmitting.value = false
  }
}

async function saveResult() {
  resultError.value = ''
  resultSuccess.value = ''

  if (resultForm.actual_duration_min !== null) {
    if (!Number.isInteger(resultForm.actual_duration_min)) {
      resultError.value = 'Фактическая длительность должна быть целым числом.'
      return
    }
    if (resultForm.actual_duration_min < 1 || resultForm.actual_duration_min > 600) {
      resultError.value = 'Фактическая длительность должна быть в диапазоне от 1 до 600 минут.'
      return
    }
  }

  resultSubmitting.value = true

  try {
    await visitApi.saveResult(appointmentId, {
      actual_service_summary: toNullableText(resultForm.actual_service_summary),
      materials_used: toNullableText(resultForm.materials_used),
      result_notes: toNullableText(resultForm.result_notes),
      actual_duration_min: resultForm.actual_duration_min,
    })
    resultSuccess.value = 'Результат сохранен.'
  } catch (err) {
    resultError.value = err instanceof Error ? err.message : 'Ошибка сохранения результата.'
  } finally {
    resultSubmitting.value = false
  }
}

async function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) {
    return
  }

  photoError.value = ''

  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    photoError.value = 'Разрешены только JPG, PNG и WEBP файлы.'
    target.value = ''
    return
  }

  if (file.size > MAX_IMAGE_SIZE_BYTES) {
    photoError.value = 'Размер файла не должен превышать 5 МБ.'
    target.value = ''
    return
  }

  try {
    const photo = await visitApi.uploadPhoto(appointmentId, file, photos.value.length)
    photos.value.push(photo)
    target.value = ''
  } catch (err) {
    photoError.value = err instanceof Error ? err.message : 'Не удалось загрузить фото.'
  }
}

async function removePhoto(photoId: number) {
  try {
    await visitApi.deletePhoto(appointmentId, photoId)
    photos.value = photos.value.filter((item) => item.id !== photoId)
  } catch (err) {
    photoError.value = err instanceof Error ? err.message : 'Не удалось удалить фото.'
  }
}

async function savePaymentData() {
  paymentError.value = ''
  paymentSuccess.value = ''

  const amountNumber = Number(paymentForm.amount)
  if (!Number.isFinite(amountNumber)) {
    paymentError.value = 'Сумма должна быть числом.'
    return
  }
  if (amountNumber < 0) {
    paymentError.value = 'Сумма не может быть отрицательной.'
    return
  }
  if (['paid', 'partial'].includes(paymentForm.payment_status) && amountNumber <= 0) {
    paymentError.value = 'Для выбранного статуса сумма должна быть больше 0.'
    return
  }

  paymentSubmitting.value = true

  try {
    await paymentApi.save(appointmentId, {
      amount: String(amountNumber),
      payment_method: paymentForm.payment_method,
      payment_status: paymentForm.payment_status,
      comment: toNullableText(paymentForm.comment || ''),
    })
    paymentSuccess.value = 'Оплата сохранена.'
    await loadPage()
  } catch (err) {
    paymentError.value = err instanceof Error ? err.message : 'Ошибка сохранения оплаты.'
  } finally {
    paymentSubmitting.value = false
  }
}

onMounted(loadPage)
</script>
