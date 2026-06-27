<template>
  <section class="space-y-6">
    <PageHeader title="Настройки графика" subtitle="Рабочие дни, часы и разовые блокировки времени" />

    <div class="grid gap-4 xl:grid-cols-2">
      <article class="card">
        <h2 class="text-lg font-semibold text-slate-800">Базовый график</h2>

        <LoadingBlock v-if="loadingRules" text="Загружаю рабочие дни..." class="mt-4" />
        <ErrorBlock v-else-if="rulesError" class="mt-4" :message="rulesError" />

        <div v-else class="mt-4 space-y-3">
          <div v-for="rule in rules" :key="rule.id" class="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <div class="mb-2 flex items-center justify-between">
              <p class="font-semibold text-slate-700">{{ weekdayLabel(rule.weekday) }}</p>
              <label class="flex items-center gap-2 text-sm text-slate-600">
                <input
                  :checked="rule.is_working_day"
                  class="h-4 w-4 rounded border-slate-300"
                  type="checkbox"
                  @change="toggleWorking(rule)"
                />
                Рабочий день
              </label>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <input :value="rule.start_time" class="input" type="time" @change="updateTime(rule, 'start', $event)" />
              <input :value="rule.end_time" class="input" type="time" @change="updateTime(rule, 'end', $event)" />
            </div>
          </div>
        </div>
      </article>

      <article class="card">
        <h2 class="text-lg font-semibold text-slate-800">Блокировка времени</h2>

        <form class="mt-4 space-y-3" @submit.prevent="onCreateBlock">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Начало</label>
            <input v-model="blockForm.start" class="input" type="datetime-local" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Окончание</label>
            <input v-model="blockForm.end" class="input" type="datetime-local" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Причина</label>
            <input v-model="blockForm.reason" class="input" type="text" placeholder="Отпуск / личные дела" />
          </div>

          <p v-if="blockError" class="text-sm text-rose-600">{{ blockError }}</p>
          <p v-if="blockSuccess" class="text-sm text-emerald-600">{{ blockSuccess }}</p>

          <button class="btn-primary w-full" type="submit" :disabled="submittingBlock">
            {{ submittingBlock ? 'Сохранение...' : 'Добавить блокировку' }}
          </button>
        </form>

        <div class="mt-6">
          <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Активные блокировки</h3>

          <LoadingBlock v-if="loadingBlocks" text="Загружаю блокировки..." class="mt-3" />
          <ErrorBlock v-else-if="blocksError" class="mt-3" :message="blocksError" />
          <EmptyState
            v-else-if="blocks.length === 0"
            class="mt-3"
            title="Блокировок нет"
            description="График полностью открыт для записи."
          />

          <div v-else class="mt-3 space-y-2">
            <div v-for="block in blocks" :key="block.id" class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2">
              <p class="font-medium text-slate-700">{{ formatDateTime(block.start_datetime) }} - {{ formatDateTime(block.end_datetime) }}</p>
              <p class="text-sm text-slate-500">{{ block.reason || 'Без причины' }}</p>
              <button class="btn-muted mt-2" type="button" @click="removeBlock(block.id)">Удалить</button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { appointmentApi } from '@/entities/appointment'
import type { TimeOffBlock, WorkScheduleRule } from '@/entities/appointment'
import { useToastStore } from '@/shared/model/toast-store'
import EmptyState from '@/shared/ui/EmptyState.vue'
import ErrorBlock from '@/shared/ui/ErrorBlock.vue'
import LoadingBlock from '@/shared/ui/LoadingBlock.vue'
import PageHeader from '@/shared/ui/PageHeader.vue'
import { formatDateTime } from '@/shared/lib/format'

const toastStore = useToastStore()

const rules = ref<WorkScheduleRule[]>([])
const blocks = ref<TimeOffBlock[]>([])

const loadingRules = ref(true)
const loadingBlocks = ref(true)
const rulesError = ref('')
const blocksError = ref('')

const blockForm = reactive({
  start: '',
  end: '',
  reason: '',
})

const submittingBlock = ref(false)
const blockError = ref('')
const blockSuccess = ref('')

const weekdayNames = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

function weekdayLabel(index: number) {
  return weekdayNames[index] || 'День'
}

async function loadRules() {
  loadingRules.value = true
  rulesError.value = ''

  try {
    const response = await appointmentApi.getScheduleRules()
    rules.value = Array.isArray(response.results) ? response.results.filter(Boolean) : []
  } catch (err) {
    rulesError.value = err instanceof Error ? err.message : 'Не удалось загрузить график.'
  } finally {
    loadingRules.value = false
  }
}

async function loadBlocks() {
  loadingBlocks.value = true
  blocksError.value = ''

  try {
    const response = await appointmentApi.getTimeOffBlocks()
    blocks.value = response.results
  } catch (err) {
    blocksError.value = err instanceof Error ? err.message : 'Не удалось загрузить блокировки.'
  } finally {
    loadingBlocks.value = false
  }
}

async function toggleWorking(rule: WorkScheduleRule) {
  try {
    const updated = await appointmentApi.updateScheduleRule(rule.id, { is_working_day: !rule.is_working_day })
    Object.assign(rule, updated)
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

async function updateTime(rule: WorkScheduleRule, kind: 'start' | 'end', event: Event) {
  const target = event.target as HTMLInputElement
  const nextValue = target.value
  const startValue = kind === 'start' ? nextValue : rule.start_time
  const endValue = kind === 'end' ? nextValue : rule.end_time

  if (startValue && endValue && startValue >= endValue) {
    toastStore.push({
      type: 'error',
      title: 'Некорректное время',
      message: 'Время начала должно быть раньше времени окончания.',
    })
    return
  }

  try {
    const payload = kind === 'start' ? { start_time: nextValue } : { end_time: nextValue }
    const updated = await appointmentApi.updateScheduleRule(rule.id, payload)
    Object.assign(rule, updated)
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

async function onCreateBlock() {
  blockError.value = ''
  blockSuccess.value = ''

  if (!blockForm.start || !blockForm.end) {
    blockError.value = 'Укажите начало и окончание блокировки.'
    return
  }

  const startDate = new Date(blockForm.start)
  const endDate = new Date(blockForm.end)

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    blockError.value = 'Укажите корректные дату и время.'
    return
  }

  if (startDate >= endDate) {
    blockError.value = 'Начало блокировки должно быть раньше окончания.'
    return
  }

  if (blockForm.reason.trim().length > 255) {
    blockError.value = 'Причина не должна превышать 255 символов.'
    return
  }

  submittingBlock.value = true

  try {
    await appointmentApi.createTimeOffBlock({
      start_datetime: startDate.toISOString(),
      end_datetime: endDate.toISOString(),
      reason: blockForm.reason.trim() || null,
    })

    blockSuccess.value = 'Блокировка добавлена.'
    blockForm.start = ''
    blockForm.end = ''
    blockForm.reason = ''
    await loadBlocks()
  } catch (err) {
    blockError.value = err instanceof Error ? err.message : 'Не удалось сохранить блокировку.'
  } finally {
    submittingBlock.value = false
  }
}

async function removeBlock(id: number) {
  try {
    await appointmentApi.deleteTimeOffBlock(id)
    await loadBlocks()
  } catch (err) {
    toastStore.push({
      type: 'error',
      title: 'Ошибка действия',
      message: err instanceof Error ? err.message : 'Не удалось выполнить действие.',
    })
  }
}

onMounted(async () => {
  await Promise.all([loadRules(), loadBlocks()])
})
</script>
