export type UserRole = 'master' | 'client'

export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  role: UserRole
  client_id?: number | null
  client_name?: string | null
}

export interface AuthResponse {
  token: string
  user: User
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  role?: UserRole
  username: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
  full_name?: string
  phone?: string
  email?: string | null
}

export interface LogoutResponse {
  detail: string
}
