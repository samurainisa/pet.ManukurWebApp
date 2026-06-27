<template>
  <main class="mx-auto min-h-screen w-full max-w-6xl px-4 py-6 md:px-6 md:py-8">
    <LoadingBlock v-if="loadingLanding" text="Загружаю страницу записи..." />
    <ErrorBlock v-else-if="pageError" :message="pageError" />

    <section v-else class="grid gap-6 lg:grid-cols-[1.4fr,0.95fr]">
      <div class="space-y-6">
        <section
          class="relative overflow-hidden rounded-3xl border border-sky-100 bg-gradient-to-br from-sky-500 via-cyan-500 to-blue-500 p-5 text-white shadow-[0_18px_50px_rgba(29,78,216,0.24)] md:p-6"
        >
          <div
            class="pointer-events-none absolute -right-16 -top-12 h-44 w-44 rounded-full bg-white/20 blur-2xl"
            aria-hidden="true"
          />
          <div
            class="pointer-events-none absolute -bottom-16 -left-10 h-48 w-48 rounded-full bg-cyan-200/25 blur-2xl"
            aria-hidden="true"
          />

          <div class="relative flex items-start gap-4">
            <img
              v-if="landing?.master.avatar"
              :src="landing.master.avatar"
              alt="Фото мастера"
              class="h-16 w-16 rounded-2xl border border-white/40 object-cover shadow-md md:h-20 md:w-20"
            />
            <div
              v-else
              class="flex h-16 w-16 items-center justify-center rounded-2xl border border-white/35 bg-white/20 text-xl font-bold md:h-20 md:w-20 md:text-2xl"
            >
              {{ masterInitials }}
            </div>

            <div class="min-w-0 flex-1">
              <p class="text-xs uppercase tracking-[0.22em] text-white/80">Профиль мастера</p>
              <h1 class="mt-1 text-2xl font-bold leading-tight text-white md:text-3xl">
                {{ landing?.master.display_name || 'Мастер маникюра' }}
              </h1>
              <p v-if="landing?.master.bio" class="mt-2 line-clamp-3 text-sm text-white/90">
                {{ landing.master.bio }}
              </p>
            </div>
          </div>

          <div class="relative mt-4 flex flex-wrap items-center gap-2 text-sm text-white/90">
            <span v-if="landing?.master.city" class="rounded-full border border-white/25 bg-white/15 px-3 py-1">
              {{ landing.master.city }}
            </span>
            <span v-if="landing?.master.address" class="rounded-full border border-white/25 bg-white/15 px-3 py-1">
              {{ landing.master.address }}
            </span>
            <span v-if="landing?.master.phone" class="rounded-full border border-white/25 bg-white/15 px-3 py-1">
              {{ landing.master.phone }}
            </span>
          </div>

          <div class="relative mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl border border-white/25 bg-white/15 p-3">
              <p class="text-xs uppercase tracking-wide text-white/75">Рейтинг</p>
              <p class="mt-1 text-xl font-semibold">{{ averageRating.toFixed(1) }} / 5</p>
              <p class="mt-1 text-sm text-yellow-200">{{ starsLine }}</p>
            </div>
            <div class="rounded-2xl border border-white/25 bg-white/15 p-3">
              <p class="text-xs uppercase tracking-wide text-white/75">Отзывов</p>
              <p class="mt-1 text-xl font-semibold">{{ landing?.reviews_count ?? 0 }}</p>
              <p class="mt-1 text-sm text-white/80">Соц.доказательство для клиентов</p>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-slate-900 md:text-xl">Услуги</h2>
              <p class="text-sm text-slate-500">Визуальные карточки с ценой и длительностью.</p>
            </div>
          </div>

          <div v-if="services.length === 0" class="mt-4">
            <EmptyState title="Услуги пока не добавлены" description="Мастер ещё не настроил список услуг." />
          </div>

          <div v-else class="mt-4 grid gap-3 sm:grid-cols-2">
            <button
              v-for="service in services"
              :key="service.id"
              type="button"
              class="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-sky-300 hover:bg-sky-50/50 hover:shadow-md"
              :class="
                selectedServiceId === service.id
                  ? 'border-sky-400 bg-sky-50 shadow-[0_10px_24px_rgba(14,116,144,0.16)]'
                  : ''
              "
              @click="selectService(service.id)"
            >
              <p class="text-base font-semibold text-slate-900">{{ service.name }}</p>
              <p class="mt-1 min-h-10 text-sm text-slate-500">
                {{ service.description || 'Аккуратный сервис с индивидуальным подходом.' }}
              </p>
              <div class="mt-3 flex flex-wrap items-center gap-2 text-sm">
                <span class="rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-700">
                  {{ formatMoney(service.base_price) }}
                </span>
                <span class="rounded-full bg-cyan-50 px-3 py-1 font-semibold text-cyan-700">
                  {{ service.base_duration_min }} мин
                </span>
              </div>
            </button>
          </div>
        </section>

        <section class="card">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-slate-900 md:text-xl">Дата и время</h2>
              <p class="text-sm text-slate-500">Календарный формат выбора слота.</p>
            </div>
            <input
              v-model="selectedDate"
              class="input max-w-52"
              type="date"
              :min="dateChips[0]?.value"
              @change="loadSlots"
            />
          </div>

          <div class="mt-3 flex gap-2 overflow-x-auto pb-1">
            <button
              v-for="chip in dateChips"
              :key="chip.value"
              type="button"
              class="shrink-0 rounded-2xl border px-3 py-2 text-left transition duration-200 hover:-translate-y-0.5 hover:shadow-sm"
              :class="
                selectedDate === chip.value
                  ? 'border-sky-400 bg-sky-50 text-sky-700'
                  : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
              "
              @click="selectDate(chip.value)"
            >
              <p class="text-xs uppercase tracking-wide">{{ chip.weekday }}</p>
              <p class="text-sm font-semibold">{{ chip.dayMonth }}</p>
            </button>
          </div>

          <div class="mt-4">
            <LoadingBlock v-if="loadingSlots" text="Проверяю доступные слоты..." />
            <EmptyState
              v-else-if="!selectedServiceId"
              title="Выберите услугу"
              description="После выбора услуги появятся доступные слоты."
            />
            <EmptyState
              v-else-if="slots.length === 0"
              title="Свободных слотов нет"
              description="Попробуйте другую дату или услугу."
            />
            <div v-else class="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
              <button
                v-for="slot in slots"
                :key="slot"
                type="button"
                class="btn-muted h-11 text-sm"
                :class="
                  selectedSlot === slot
                    ? '!border-sky-500 !bg-sky-100 !text-sky-700 !shadow-[0_8px_18px_rgba(14,116,144,0.18)]'
                    : ''
                "
                @click="selectedSlot = slot"
              >
                {{ slotTime(slot) }}
              </button>
            </div>
          </div>
        </section>

        <section class="card">
          <h2 class="text-lg font-semibold text-slate-900 md:text-xl">Фото работ</h2>
          <p class="text-sm text-slate-500">Галерея реальных результатов.</p>

          <div v-if="portfolio.length === 0" class="mt-4">
            <EmptyState title="Фото пока нет" description="Мастер скоро добавит примеры работ." />
          </div>

          <div v-else class="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
            <figure
              v-for="item in portfolio"
              :key="item.id"
              class="group overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 shadow-sm"
            >
              <img
                v-if="item.image"
                :src="item.image"
                :alt="`Фото работы: ${item.service_name}`"
                class="h-36 w-full object-cover transition duration-300 group-hover:scale-105 md:h-40"
                loading="lazy"
              />
              <div v-else class="flex h-36 items-center justify-center text-sm text-slate-500 md:h-40">
                Фото недоступно
              </div>
              <figcaption class="p-2 text-xs font-medium text-slate-600">
                {{ item.service_name }}
              </figcaption>
            </figure>
          </div>
        </section>

        <section class="card">
          <h2 class="text-lg font-semibold text-slate-900 md:text-xl">Отзывы</h2>
          <p class="text-sm text-slate-500">Рейтинг и впечатления клиентов.</p>

          <div v-if="reviews.length === 0" class="mt-4">
            <EmptyState title="Пока нет отзывов" description="Будьте первым клиентом, который оставит отзыв." />
          </div>

          <div v-else class="mt-4 space-y-3">
            <article
              v-for="review in reviews"
              :key="review.id"
              class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-sky-300 hover:shadow-md"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-sm font-semibold text-slate-900">{{ review.client_name }}</p>
                  <p class="text-xs text-slate-500">{{ reviewDate(review.created_at) }}</p>
                </div>
                <p class="text-sm text-amber-500">{{ reviewStars(review.rating) }}</p>
              </div>
              <p class="mt-2 text-sm leading-relaxed text-slate-700">{{ review.text }}</p>
            </article>
          </div>
        </section>
      </div>

      <aside class="space-y-4 lg:sticky lg:top-5 lg:self-start">
        <section class="card">
          <h2 class="text-lg font-semibold text-slate-900">Оформление записи</h2>
          <p class="text-sm text-slate-500">Заполните контакты и отправьте заявку.</p>

          <div class="mt-3 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
            <p>
              <span class="font-medium text-slate-900">Услуга:</span>
              {{ selectedService?.name || 'Не выбрана' }}
            </p>
            <p class="mt-1">
              <span class="font-medium text-slate-900">Дата:</span>
              {{ selectedDate ? formatDate(selectedDate) : 'Не выбрана' }}
            </p>
            <p class="mt-1">
              <span class="font-medium text-slate-900">Время:</span>
              {{ selectedSlot ? slotTime(selectedSlot) : 'Не выбрано' }}
            </p>
          </div>

          <form class="mt-4 space-y-3" @submit.prevent="onSubmit">
            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Имя</label>
              <input v-model="form.full_name" class="input" required type="text" />
            </div>

            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Телефон</label>
              <input v-model="form.phone" class="input" required type="tel" />
            </div>

            <div>
              <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Комментарий
              </label>
              <textarea
                v-model="form.comment"
                class="input min-h-24"
                placeholder="Например: нужен дизайн, укрепление и т.д."
              />
            </div>

            <input v-model="form.website" tabindex="-1" autocomplete="off" class="hidden" type="text" />

            <p v-if="submitError" class="text-sm text-rose-600">{{ submitError }}</p>

            <button class="btn-primary w-full py-3 text-sm md:text-base" type="submit" :disabled="submitting || !selectedSlot">
              {{ submitting ? 'Отправка...' : 'Записаться' }}
            </button>
          </form>
        </section>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { appointmentApi } from '@/entities/appointment'
import { publicBookingApi } from '@/entities/public-booking'
import type { PublicLanding } from '@/entities/public-booking'
import type { Service } from '@/entities/service'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import { formatDate, formatMoney } from '@/shared/lib/format'
import { normalizeSpaces, toNullableText, validatePhone, validateRequiredText } from '@/shared/lib/validation'

type DateChip = {
  value: string
  weekday: string
  dayMonth: string
}

const router = useRouter()

const loadingLanding = ref(true)
const loadingSlots = ref(false)
const submitting = ref(false)
const pageError = ref('')
const submitError = ref('')

const landing = ref<PublicLanding | null>(null)
const selectedServiceId = ref(0)
const selectedDate = ref(toDateString(addDays(new Date(), 1)))
const selectedSlot = ref('')
const slots = ref<string[]>([])

const form = reactive({
  full_name: '',
  phone: '',
  comment: '',
  website: '',
})

const services = computed(() => landing.value?.services ?? [])
const portfolio = computed(() => (landing.value?.portfolio ?? []).slice(0, 9))
const reviews = computed(() => (landing.value?.reviews ?? []).slice(0, 6))
const selectedService = computed<Service | undefined>(() => services.value.find((item) => item.id === selectedServiceId.value))
const averageRating = computed(() => landing.value?.rating_avg ?? 0)
const starsLine = computed(() => reviewStars(Math.round(averageRating.value)))

const masterInitials = computed(() => {
  const name = landing.value?.master.display_name || 'Мастер'
  const parts = name
    .split(/\s+/)
    .map((item) => item.trim())
    .filter(Boolean)
  if (parts.length === 0) {
    return 'М'
  }
  return `${parts[0][0]}${parts[1]?.[0] ?? ''}`.toUpperCase()
})

const dateChips = computed<DateChip[]>(() => {
  const start = new Date()
  start.setHours(0, 0, 0, 0)
  return Array.from({ length: 14 }, (_, index) => {
    const day = addDays(start, index)
    return {
      value: toDateString(day),
      weekday: day.toLocaleDateString('ru-RU', { weekday: 'short' }).replace('.', ''),
      dayMonth: day.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' }),
    }
  })
})

function addDays(base: Date, days: number) {
  const next = new Date(base)
  next.setDate(next.getDate() + days)
  return next
}

function toDateString(value: Date) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function slotTime(slotIso: string) {
  return new Date(slotIso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function reviewStars(rating: number) {
  const safe = Math.max(0, Math.min(5, Math.round(rating)))
  return `${'★'.repeat(safe)}${'☆'.repeat(5 - safe)}`
}

function reviewDate(value: string) {
  return new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}

function selectService(serviceId: number) {
  selectedServiceId.value = serviceId
  void loadSlots()
}

function selectDate(date: string) {
  selectedDate.value = date
  void loadSlots()
}

async function loadLanding() {
  loadingLanding.value = true
  pageError.value = ''

  try {
    const response = await publicBookingApi.getLanding()
    landing.value = response

    if (!response.services.length) {
      slots.value = []
      selectedSlot.value = ''
      return
    }

    selectedServiceId.value = response.services[0].id
    await loadSlots()
  } catch (err) {
    pageError.value = err instanceof Error ? err.message : 'Не удалось загрузить страницу записи.'
  } finally {
    loadingLanding.value = false
  }
}

async function loadSlots() {
  if (!selectedServiceId.value || !selectedDate.value) {
    slots.value = []
    selectedSlot.value = ''
    return
  }

  loadingSlots.value = true
  submitError.value = ''
  selectedSlot.value = ''

  try {
    const response = await appointmentApi.getPublicAvailableSlots(selectedServiceId.value, selectedDate.value)
    slots.value = response.slots
  } catch (err) {
    slots.value = []
    submitError.value = err instanceof Error ? err.message : 'Не удалось загрузить доступные слоты.'
  } finally {
    loadingSlots.value = false
  }
}

async function onSubmit() {
  const nameError = validateRequiredText(form.full_name, 'Имя', 2)
  if (nameError) {
    submitError.value = nameError
    return
  }

  const phoneError = validatePhone(form.phone)
  if (phoneError) {
    submitError.value = phoneError
    return
  }

  if (!selectedServiceId.value) {
    submitError.value = 'Выберите услугу.'
    return
  }

  if (!selectedDate.value) {
    submitError.value = 'Выберите дату записи.'
    return
  }

  if (!selectedSlot.value) {
    submitError.value = 'Выберите доступное время.'
    return
  }

  const slotDate = selectedSlot.value.slice(0, 10)
  const slotTimeValue = selectedSlot.value.slice(11, 16)
  if (!slotDate || !slotTimeValue || slotTimeValue.length !== 5) {
    submitError.value = 'Некорректный слот. Выберите время ещё раз.'
    return
  }

  submitting.value = true
  submitError.value = ''

  try {
    const response = await publicBookingApi.createBooking({
      service_id: selectedServiceId.value,
      date: slotDate,
      time: slotTimeValue,
      full_name: normalizeSpaces(form.full_name),
      phone: normalizeSpaces(form.phone),
      comment: toNullableText(form.comment) ?? '',
      website: form.website,
    })

    router.push({ path: '/book/success', query: { id: String(response.id) } })
  } catch (err) {
    submitError.value = err instanceof Error ? err.message : 'Не удалось отправить заявку.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadLanding)
</script>
