<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-10">
    <div class="w-full max-w-md rounded-3xl bg-white p-7 shadow-[0_20px_50px_rgba(24,40,46,0.12)]">
      <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Личный кабинет</p>
      <h1 class="mt-2 text-2xl font-bold text-slate-900">Вход</h1>
      <p class="mt-1 text-sm text-slate-500">Введите логин и пароль для входа.</p>

      <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Логин</label>
          <input v-model="form.username" class="input" type="text" autocomplete="username" required />
        </div>

        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Пароль</label>
          <input
            v-model="form.password"
            class="input"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>

        <button class="btn-primary w-full" type="submit" :disabled="loading">
          {{ loading ? 'Выполняю вход...' : 'Войти' }}
        </button>
      </form>

      <div class="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
        <p class="font-semibold text-slate-700">Демо-данные мастера</p>
        <p class="mt-1">Логин: <code>master</code></p>
        <p>Пароль: <code>master12345</code></p>
      </div>

      <p class="mt-4 text-xs text-slate-500">
        Нет аккаунта?
        <RouterLink class="text-link" to="/register">Зарегистрироваться</RouterLink>
      </p>

      <p class="mt-2 text-xs text-slate-400">
        Публичная запись клиентов:
        <RouterLink class="text-link" to="/book">/book</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { defaultPathByRole } from '@/app/router/paths'
import { useSessionStore } from '@/entities/session'
import { normalizeSpaces } from '@/shared/lib/validation'

const router = useRouter()
const sessionStore = useSessionStore()

const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
})

function pathByRole(role: 'master' | 'client' | undefined) {
  return defaultPathByRole(role)
}

async function onSubmit() {
  error.value = ''

  const username = normalizeSpaces(form.username)
  if (!username) {
    error.value = 'Введите логин.'
    return
  }
  if (!form.password) {
    error.value = 'Введите пароль.'
    return
  }

  loading.value = true

  try {
    const response = await sessionStore.login({ username, password: form.password })
    router.push(pathByRole(response.user.role))
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось выполнить вход.'
  } finally {
    loading.value = false
  }
}
</script>
