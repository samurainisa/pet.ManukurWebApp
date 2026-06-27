import { httpClient } from '@/shared/api/HttpClient'

import { VISIT_ROUTES } from './routes'
import type { VisitPhoto, VisitResult, VisitResultPayload } from '../model/types'

export class VisitApi {
  getResult(appointmentId: number): Promise<VisitResult> {
    return httpClient.get<VisitResult>(VISIT_ROUTES.result(appointmentId))
  }

  saveResult(appointmentId: number, payload: VisitResultPayload): Promise<VisitResult> {
    return httpClient.put<VisitResult>(VISIT_ROUTES.result(appointmentId), payload)
  }

  uploadPhoto(appointmentId: number, file: File, sortOrder = 0): Promise<VisitPhoto> {
    const body = new FormData()
    body.append('image', file)
    body.append('sort_order', String(sortOrder))

    return httpClient.post<VisitPhoto>(VISIT_ROUTES.photos(appointmentId), body)
  }

  deletePhoto(appointmentId: number, photoId: number): Promise<null> {
    return httpClient.delete<null>(VISIT_ROUTES.photo(appointmentId, photoId))
  }
}

export const visitApi = new VisitApi()
