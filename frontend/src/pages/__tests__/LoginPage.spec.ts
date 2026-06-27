import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LoginPage from '../LoginPage.vue'

const pushMock = vi.fn()
const loginMock = vi.fn()

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRouter: () => ({ push: pushMock }),
    RouterLink: {
      template: '<a><slot /></a>',
    },
  }
})

vi.mock('@/entities/session', async () => {
  const actual = await vi.importActual<typeof import('@/entities/session')>('@/entities/session')
  return {
    ...actual,
    useSessionStore: () => ({
      login: (...args: unknown[]) => loginMock(...args),
    }),
  }
})

describe('LoginPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    loginMock.mockResolvedValue({
      token: 'token-1',
      user: {
        id: 1,
        username: 'master',
        first_name: '',
        last_name: '',
        role: 'master',
      },
    })
  })

  it('submits credentials and redirects to dashboard', async () => {
    const wrapper = mount(LoginPage)

    await wrapper.find('input[type="text"]').setValue('master')
    await wrapper.find('input[type="password"]').setValue('secret123')
    await wrapper.find('form').trigger('submit.prevent')

    await flushPromises()

    expect(loginMock).toHaveBeenCalledWith({ username: 'master', password: 'secret123' })
    expect(pushMock).toHaveBeenCalledWith('/dashboard')
  })
})
