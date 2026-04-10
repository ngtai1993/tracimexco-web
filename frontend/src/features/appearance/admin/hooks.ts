'use client'
import { useState, useEffect, useCallback } from 'react'
import { tokenApi, assetApi, revalidateAppearanceCache } from './api'
import type {
  ColorTokenAdmin,
  MediaAssetAdmin,
  CreateTokenInput,
  UpdateTokenInput,
  UpdateAssetInput,
} from './types'

function getListErrorMessage(err: unknown, entity: 'token' | 'asset'): string {
  const status = (err as { response?: { status?: number } })?.response?.status
  if (status === 401) {
    return 'Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại bằng tài khoản admin.'
  }
  if (status === 403) {
    return 'Bạn không có quyền truy cập dữ liệu appearance. Cần tài khoản admin để thao tác.'
  }
  return entity === 'token'
    ? 'Không thể tải danh sách token'
    : 'Không thể tải danh sách assets'
}

function hasAccessToken(): boolean {
  if (typeof window === 'undefined') return true
  return Boolean(localStorage.getItem('access_token'))
}

// ─── Token hooks ──────────────────────────────────────────────────────────────

export function useTokens(params?: { include_inactive?: boolean }) {
  const [tokens, setTokens] = useState<ColorTokenAdmin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!hasAccessToken()) {
      setTokens([])
      setLoading(false)
      setError('Bạn chưa đăng nhập trên trình duyệt này. Vui lòng đăng xuất và đăng nhập lại bằng tài khoản admin.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const res = await tokenApi.list(params)
      setTokens(res.data.data)
    } catch (err: unknown) {
      setError(getListErrorMessage(err, 'token'))
    } finally {
      setLoading(false)
    }
  }, [params?.include_inactive]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetch() }, [fetch])

  return { tokens, loading, error, refetch: fetch }
}

export function useCreateToken() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | null>(null)

  const create = async (data: CreateTokenInput): Promise<ColorTokenAdmin | null> => {
    setLoading(true)
    setError(null)
    setFieldErrors(null)
    try {
      const res = await tokenApi.create(data)
      await revalidateAppearanceCache()
      return res.data.data
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string; errors?: Record<string, string[]> } } }
      setError(e.response?.data?.message ?? 'Tạo token thất bại')
      setFieldErrors(e.response?.data?.errors ?? null)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error, fieldErrors }
}

export function useUpdateToken() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | null>(null)

  const update = async (id: string, data: UpdateTokenInput): Promise<ColorTokenAdmin | null> => {
    setLoading(true)
    setError(null)
    setFieldErrors(null)
    try {
      const res = await tokenApi.update(id, data)
      await revalidateAppearanceCache()
      return res.data.data
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string; errors?: Record<string, string[]> } } }
      setError(e.response?.data?.message ?? 'Cập nhật token thất bại')
      setFieldErrors(e.response?.data?.errors ?? null)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { update, loading, error, fieldErrors }
}

export function useDeleteToken() {
  const [loading, setLoading] = useState(false)

  const remove = async (id: string): Promise<boolean> => {
    setLoading(true)
    try {
      await tokenApi.delete(id)
      await revalidateAppearanceCache()
      return true
    } catch {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { remove, loading }
}

// ─── Asset hooks ──────────────────────────────────────────────────────────────

export function useAssets(params?: { include_inactive?: boolean }) {
  const [assets, setAssets] = useState<MediaAssetAdmin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!hasAccessToken()) {
      setAssets([])
      setLoading(false)
      setError('Bạn chưa đăng nhập trên trình duyệt này. Vui lòng đăng xuất và đăng nhập lại bằng tài khoản admin.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const res = await assetApi.list(params)
      setAssets(res.data.data)
    } catch (err: unknown) {
      setError(getListErrorMessage(err, 'asset'))
    } finally {
      setLoading(false)
    }
  }, [params?.include_inactive]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetch() }, [fetch])

  return { assets, loading, error, refetch: fetch }
}

export function useCreateAsset() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | null>(null)

  const create = async (data: FormData): Promise<MediaAssetAdmin | null> => {
    setLoading(true)
    setError(null)
    setFieldErrors(null)
    try {
      const res = await assetApi.create(data)
      await revalidateAppearanceCache()
      return res.data.data
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string; errors?: Record<string, string[]> } } }
      setError(e.response?.data?.message ?? 'Upload thất bại')
      setFieldErrors(e.response?.data?.errors ?? null)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error, fieldErrors }
}

export function useUpdateAsset() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | null>(null)

  const update = async (
    id: string,
    data: FormData | UpdateAssetInput
  ): Promise<MediaAssetAdmin | null> => {
    setLoading(true)
    setError(null)
    setFieldErrors(null)
    try {
      const res = await assetApi.update(id, data)
      await revalidateAppearanceCache()
      return res.data.data
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string; errors?: Record<string, string[]> } } }
      setError(e.response?.data?.message ?? 'Cập nhật asset thất bại')
      setFieldErrors(e.response?.data?.errors ?? null)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { update, loading, error, fieldErrors }
}

export function useDeleteAsset() {
  const [loading, setLoading] = useState(false)

  const remove = async (id: string): Promise<boolean> => {
    setLoading(true)
    try {
      await assetApi.delete(id)
      await revalidateAppearanceCache()
      return true
    } catch {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { remove, loading }
}
