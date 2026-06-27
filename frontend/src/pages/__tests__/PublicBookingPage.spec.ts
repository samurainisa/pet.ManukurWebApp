import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import PublicBookingPage from '../PublicBookingPage.vue'

const pushMock = vi.fn()
const createPublicBookingMock = vi.fn()
const getPublicLandingMock = vi.fn()
const getPublicAvailableSlotsMock = vi.fn()

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')
  return {
    ...actual,
    useRouter: () => ({ push: pushMock }),
  }
})

vi.mock('@/entities/public-booking', () => ({
  publicBookingApi: {
    createBooking: (...args: unknown[]) => createPublicBookingMock(...args),
    getLanding: (...args: unknown[]) => getPublicLandingMock(...args),
  },
}))

vi.mock('@/entities/appointment', () => ({
  appointmentApi: {
    getPublicAvailableSlots: (...args: unknown[]) => getPublicAvailableSlotsMock(...args),
  },
}))

function tomorrowDateString(): string {
  const date = new Date()
  date.setDate(date.getDate() + 1)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function tomorrowIsoSlot(time: string): string {
  return `${tomorrowDateString()}T${time}:00`
}

describe('PublicBookingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    getPublicLandingMock.mockResolvedValue({
      master: {
        display_name: 'Диана Пшенова',
        city: 'Санкт-Петербург',
        address: 'Малая Бухарестская, 12',
        phone: '+7 (912) 000-00-00',
        bio: 'Без ожидания подтверждения',
        telegram: null,
        avatar: null,
      },
      rating_avg: 4.9,
      reviews_count: 12,
      reviews: [],
      portfolio: [],
      services: [
        {
          id: 1,
          name: 'Маникюр',
          description: null,
          base_duration_min: 60,
          base_price: '1500.00',
          is_active: true,
          sort_order: 0,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
    })

    getPublicAvailableSlotsMock.mockResolvedValue({
      service_id: 1,
      date: tomorrowDateString(),
      slots: [tomorrowIsoSlot('10:00'), tomorrowIsoSlot('11:00')],
    })

    createPublicBookingMock.mockResolvedValue({ id: 99 })
  })

  it('submits public booking form', async () => {
    const wrapper = mount(PublicBookingPage)

    await flushPromises()
    await flushPromises()

    const slotButtons = wrapper.findAll('button.btn-muted.h-11')
    expect(slotButtons.length).toBeGreaterThan(0)
    await slotButtons[0].trigger('click')

    await wrapper.find('input[type="text"].input').setValue('Анна')
    await wrapper.find('input[type="tel"]').setValue('+79990000000')
    await wrapper.find('form').trigger('submit.prevent')

    await flushPromises()

    expect(createPublicBookingMock).toHaveBeenCalled()
    expect(pushMock).toHaveBeenCalledWith({ path: '/book/success', query: { id: '99' } })
  })
})
