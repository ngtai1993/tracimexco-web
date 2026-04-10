import { apiClient } from '@/lib/api'
import type { ApiResponse } from '@/types/api'
import type {
  ColorTokenAdmin,
  MediaAssetAdmin,
  CreateTokenInput,
  UpdateTokenInput,
  UpdateAssetInput,
} from './types'

// ─── Color Tokens ─────────────────────────────────────────────────────────────

export const tokenApi = {
  list: (params?: { include_inactive?: boolean }) =>
    apiClient.get<ApiResponse<ColorTokenAdmin[]>>('/api/v1/appearance/tokens/', { params }),

  get: (id: string) =>
    apiClient.get<ApiResponse<ColorTokenAdmin>>(`/api/v1/appearance/tokens/${id}/`),

  create: (data: CreateTokenInput) =>
    apiClient.post<ApiResponse<ColorTokenAdmin>>('/api/v1/appearance/tokens/', data),

  update: (id: string, data: UpdateTokenInput) =>
    apiClient.patch<ApiResponse<ColorTokenAdmin>>(`/api/v1/appearance/tokens/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/api/v1/appearance/tokens/${id}/`),
}

// ─── Media Assets ─────────────────────────────────────────────────────────────

export const assetApi = {
  list: (params?: { include_inactive?: boolean }) =>
    apiClient.get<ApiResponse<MediaAssetAdmin[]>>('/api/v1/appearance/assets/', { params }),

  get: (id: string) =>
    apiClient.get<ApiResponse<MediaAssetAdmin>>(`/api/v1/appearance/assets/${id}/`),

  /** file upload — nhận FormData */
  create: (data: FormData) =>
    apiClient.post<ApiResponse<MediaAssetAdmin>>('/api/v1/appearance/assets/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  /** update — FormData nếu có file, plain object nếu chỉ metadata */
  update: (id: string, data: FormData | UpdateAssetInput) =>
    apiClient.patch<ApiResponse<MediaAssetAdmin>>(`/api/v1/appearance/assets/${id}/`, data, {
      headers:
        data instanceof FormData
          ? { 'Content-Type': 'multipart/form-data' }
          : { 'Content-Type': 'application/json' },
    }),

  delete: (id: string) =>
    apiClient.delete(`/api/v1/appearance/assets/${id}/`),
}

// ─── Revalidate Next.js cache ─────────────────────────────────────────────────

export async function revalidateAppearanceCache(): Promise<void> {
  const secret = process.env.NEXT_PUBLIC_REVALIDATE_SECRET
  if (!secret) return
  try {
    await fetch(`/api/revalidate?secret=${encodeURIComponent(secret)}`, {
      method: 'POST',
    })
  } catch {
    // không block UI
  }
}
