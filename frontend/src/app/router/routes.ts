import type { RouteRecordRaw } from 'vue-router'

import { ROUTE_PATHS } from './paths'

export const appRoutes: RouteRecordRaw[] = [
  {
    path: ROUTE_PATHS.login,
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { public: true, title: 'Login' },
  },
  {
    path: ROUTE_PATHS.register,
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { public: true, title: 'Registration' },
  },
  {
    path: ROUTE_PATHS.book,
    name: 'book',
    component: () => import('@/pages/PublicBookingPage.vue'),
    meta: { public: true, title: 'Public booking' },
  },
  {
    path: ROUTE_PATHS.bookSuccess,
    name: 'book-success',
    component: () => import('@/pages/PublicBookingSuccessPage.vue'),
    meta: { public: true, title: 'Booking created' },
  },
  {
    path: '/',
    component: () => import('@/pages/PrivateLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: ROUTE_PATHS.dashboard },
      {
        path: ROUTE_PATHS.dashboard,
        name: 'dashboard',
        component: () => import('@/pages/DashboardPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Дашборд' },
      },
      {
        path: ROUTE_PATHS.clients,
        name: 'clients',
        component: () => import('@/pages/ClientsPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Клиенты' },
      },
      {
        path: ROUTE_PATHS.clientDetail,
        name: 'client-detail',
        component: () => import('@/pages/ClientDetailPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Карта клиента' },
      },
      {
        path: ROUTE_PATHS.services,
        name: 'services',
        component: () => import('@/pages/ServicesPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Услуги' },
      },
      {
        path: ROUTE_PATHS.schedule,
        name: 'schedule',
        component: () => import('@/pages/SchedulePage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Расписание' },
      },
      {
        path: ROUTE_PATHS.appointmentDetail,
        name: 'appointment-detail',
        component: () => import('@/pages/AppointmentDetailPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Карточка записи' },
      },
      {
        path: ROUTE_PATHS.analytics,
        name: 'analytics',
        component: () => import('@/pages/AnalyticsPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'Аналитика' },
      },
      {
        path: ROUTE_PATHS.scheduleSettings,
        name: 'schedule-settings',
        component: () => import('@/pages/ScheduleSettingsPage.vue'),
        meta: { requiresAuth: true, roles: ['master'], title: 'График работы' },
      },
      {
        path: ROUTE_PATHS.clientBook,
        name: 'client-book',
        component: () => import('@/pages/ClientBookingPage.vue'),
        meta: { requiresAuth: true, roles: ['client'], title: 'Запись' },
      },
      {
        path: ROUTE_PATHS.clientAppointments,
        name: 'client-appointments',
        component: () => import('@/pages/ClientAppointmentsPage.vue'),
        meta: { requiresAuth: true, roles: ['client'], title: 'Мои визиты' },
      },
      {
        path: ROUTE_PATHS.clientNotifications,
        name: 'client-notifications',
        component: () => import('@/pages/ClientNotificationsPage.vue'),
        meta: { requiresAuth: true, roles: ['client'], title: 'Уведомления' },
      },
    ],
  },
]
