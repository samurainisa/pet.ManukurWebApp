<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-10">
    <div class="w-full max-w-lg rounded-3xl bg-white p-7 shadow-[0_20px_50px_rgba(24,40,46,0.12)]">
      <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Регистрация</p>
      <h1 class="mt-2 text-2xl font-bold text-slate-900">Создание аккаунта</h1>
      <p class="mt-1 text-sm text-slate-500">Выберите роль и заполните данные.</p>

      <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Роль</label>
          <select v-model="form.role" class="input">
            <option value="master">Мастер</option>
            <option value="client">Клиент</option>
          </select>
        </div>

        <div v-if="isMasterRole" class="grid gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Имя</label>
            <input v-model="form.first_name" class="input" type="text" autocomplete="given-name" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Фамилия</label>
            <input v-model="form.last_name" class="input" type="text" autocomplete="family-name" />
          </div>
        </div>

        <div v-else class="grid gap-3 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Имя клиента</label>
            <input v-model="form.full_name" class="input" type="text" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Телефон</label>
            <input v-model="form.phone" class="input" type="tel" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
            <input v-model="form.email" class="input" type="email" />
          </div>
        </div>

        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Логин</label>
          <input v-model="form.username" class="input" type="text" autocomplete="username" required />
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Пароль</label>
            <input v-model="form.password" class="input" type="password" autocomplete="new-password" required />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Подтверждение</label>
            <input
              v-model="form.password_confirm"
              class="input"
              type="password"
              autocomplete="new-password"
              required
            />
          </div>
        </div>

        <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>

        <button class="btn-primary w-full" type="submit" :disabled="loading">
          {{ loading ? 'Создаю аккаунт...' : 'Создать аккаунт' }}
        </button>
      </form>

      <p class="mt-4 text-sm text-slate-500">
        Уже есть аккаунт?
        <RouterLink class="text-link" to="/login">Войти</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { defaultPathByRole } from '@/app/router/paths'
import { useSessionStore } from '@/entities/session'
import { useToastStore } from '@/shared/model/toast-store'
import { normalizeSpaces, validateOptionalEmail, validatePhone, validateRequiredText } from '@/shared/lib/validation'

const router = useRouter()
const sessionStore = useSessionStore()
const toastStore = useToastStore()

const loading = ref(false)
const error = ref('')

const form = reactive({
  role: 'master' as 'master' | 'client',
  username: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  full_name: '',
  phone: '',
  email: '',
})

const isMasterRole = computed(() => form.role === 'master')

function pathByRole(role: 'master' | 'client' | undefined) {
  return defaultPathByRole(role)
}

async function onSubmit() {
  error.value = ''

  const username = normalizeSpaces(form.username)
  if (!username) {
    error.value = 'Укажите логин.'
    return
  }
  if (username.length < 3) {
    error.value = 'Логин должен содержать минимум 3 символа.'
    return
  }
  if (/\s/.test(username)) {
    error.value = 'Логин не должен содержать пробелы.'
    return
  }
  if (!form.password) {
    error.value = 'Укажите пароль.'
    return
  }
  if (form.password.length < 8) {
    error.value = 'Пароль должен содержать минимум 8 символов.'
    return
  }
  if (form.password !== form.password_confirm) {
    error.value = 'Пароли не совпадают.'
    return
  }

  if (!isMasterRole.value) {
    const nameError = validateRequiredText(form.full_name, 'Имя клиента', 2)
    if (nameError) {
      error.value = nameError
      return
    }
    const phoneError = validatePhone(form.phone)
    if (phoneError) {
      error.value = phoneError
      return
    }
    const emailError = validateOptionalEmail(form.email)
    if (emailError) {
      error.value = emailError
      return
    }
  }

  loading.value = true

  try {
    const response = await sessionStore.register({
      role: form.role,
      username,
      password: form.password,
      password_confirm: form.password_confirm,
      first_name: isMasterRole.value ? normalizeSpaces(form.first_name) : '',
      last_name: isMasterRole.value ? normalizeSpaces(form.last_name) : '',
      full_name: !isMasterRole.value ? normalizeSpaces(form.full_name) : '',
      phone: !isMasterRole.value ? normalizeSpaces(form.phone) : '',
      email: !isMasterRole.value ? normalizeSpaces(form.email) || null : null,
    })
    toastStore.push({
      type: 'success',
      title: 'Успешно',
      message: form.role === 'client' ? 'Аккаунт клиента создан.' : 'Аккаунт мастера создан.',
    })
    router.push(pathByRole(response.user.role))
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось зарегистрировать аккаунт.'
  } finally {
    loading.value = false
  }
}
</script>
