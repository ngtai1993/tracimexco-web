export interface ApiResponse<T = unknown> {
  data: T
  message: string
  errors?: Record<string, string[]> | null
}

export interface PaginatedResponse<T> {
  data: {
    results: T[]
    count: number
    next: string | null
    previous: string | null
  }
  message: string
}

export type FieldErrors = Record<string, string[]>

export interface ActionResult<T = void> {
  success: boolean
  data?: T
  error?: string
  fieldErrors?: FieldErrors
}
