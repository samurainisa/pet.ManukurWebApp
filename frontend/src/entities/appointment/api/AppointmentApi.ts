import { httpClient } from '@/shared/api/HttpClient'
import type { PaginatedResponse } from '@/shared/types/pagination'

import { APPOINTMENT_ROUTES } from './routes'
import type {
  Appointment,
  AppointmentListParams,
  CalendarDayResponse,
  CalendarWeekResponse,
  CancelPayload,
  ReschedulePayload,
  SlotsResponse,
  TimeOffBlock,
  TimeOffPayload,
  WorkScheduleRule,
} from '../model/types'

export class AppointmentApi {
  getList(params: AppointmentListParams = {}): Promise<PaginatedResponse<Appointment>> {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value) {
        query.set(key, value)
      }
    })
    return httpClient.get<PaginatedResponse<Appointment>>(
      `${APPOINTMENT_ROUTES.list}?${query.toString()}`,
    )
  }

  create(payload: Partial<Appointment>): Promise<Appointment> {
    return httpClient.post<Appointment>(APPOINTMENT_ROUTES.list, payload)
  }

  getById(id: number): Promise<Appointment> {
    return httpClient.get<Appointment>(APPOINTMENT_ROUTES.detail(id))
  }

  update(id: number, payload: Partial<Appointment>): Promise<Appointment> {
    return httpClient.patch<Appointment>(APPOINTMENT_ROUTES.detail(id), payload)
  }

  cancel(id: number, payload: CancelPayload): Promise<Appointment> {
    return httpClient.post<Appointment>(APPOINTMENT_ROUTES.cancel(id), payload)
  }

  reschedule(id: number, payload: ReschedulePayload): Promise<Appointment> {
    return httpClient.post<Appointment>(APPOINTMENT_ROUTES.reschedule(id), payload)
  }

  markNoShow(id: number): Promise<Appointment> {
    return httpClient.post<Appointment>(APPOINTMENT_ROUTES.markNoShow(id))
  }

  getCalendarDay(date: string): Promise<CalendarDayResponse> {
    return httpClient.get<CalendarDayResponse>(`${APPOINTMENT_ROUTES.calendarDay}?date=${date}`)
  }

  getCalendarWeek(date: string): Promise<CalendarWeekResponse> {
    return httpClient.get<CalendarWeekResponse>(`${APPOINTMENT_ROUTES.calendarWeek}?date=${date}`)
  }

  getAvailableSlots(serviceId: number, date: string): Promise<SlotsResponse> {
    return httpClient.get<SlotsResponse>(
      `${APPOINTMENT_ROUTES.availableSlots}?service_id=${serviceId}&date=${date}`,
    )
  }

  getPublicAvailableSlots(serviceId: number, date: string): Promise<SlotsResponse> {
    return httpClient.get<SlotsResponse>(
      `${APPOINTMENT_ROUTES.publicAvailableSlots}?service_id=${serviceId}&date=${date}`,
      { withAuth: false },
    )
  }

  getScheduleRules(): Promise<PaginatedResponse<WorkScheduleRule>> {
    return httpClient.get<PaginatedResponse<WorkScheduleRule>>(APPOINTMENT_ROUTES.scheduleRules)
  }

  updateScheduleRule(id: number, payload: Partial<WorkScheduleRule>): Promise<WorkScheduleRule> {
    return httpClient.patch<WorkScheduleRule>(APPOINTMENT_ROUTES.scheduleRule(id), payload)
  }

  getTimeOffBlocks(): Promise<PaginatedResponse<TimeOffBlock>> {
    return httpClient.get<PaginatedResponse<TimeOffBlock>>(APPOINTMENT_ROUTES.timeOffBlocks)
  }

  createTimeOffBlock(payload: TimeOffPayload): Promise<TimeOffBlock> {
    return httpClient.post<TimeOffBlock>(APPOINTMENT_ROUTES.timeOffBlocks, payload)
  }

  deleteTimeOffBlock(id: number): Promise<null> {
    return httpClient.delete<null>(APPOINTMENT_ROUTES.timeOffBlock(id))
  }
}

export const appointmentApi = new AppointmentApi()
