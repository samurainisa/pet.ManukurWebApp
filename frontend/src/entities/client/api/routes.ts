export const CLIENT_ROUTES = {
  list: '/clients/',
  detail: (id: number) => `/clients/${id}/`,
  history: (id: number) => `/clients/${id}/history/`,
} as const
