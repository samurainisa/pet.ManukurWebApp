export const VISIT_ROUTES = {
  result: (appointmentId: number) => `/appointments/${appointmentId}/result/`,
  photos: (appointmentId: number) => `/appointments/${appointmentId}/photos/`,
  photo: (appointmentId: number, photoId: number) =>
    `/appointments/${appointmentId}/photos/${photoId}/`,
} as const
