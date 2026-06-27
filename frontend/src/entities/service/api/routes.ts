export const SERVICE_ROUTES = {
  list: '/services/',
  detail: (id: number) => `/services/${id}/`,
  publicList: '/public/services/',
} as const
