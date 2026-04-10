export interface User {
  id: string
  email: string
  full_name: string
  date_joined: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  full_name: string
  password: string
  password_confirm: string
}

export interface AuthTokens {
  access: string
  refresh: string
  user: User
}

export interface ChangePasswordPayload {
  old_password: string
  new_password: string
  new_password_confirm: string
}
