'use client'
import { useAppearanceContext } from './context'
import type { MediaAssetRef } from '@/types/appearance'

/** Toàn bộ config — dùng từ client component sau khi wrap AppearanceProvider */
export function useAppearance() {
  return useAppearanceContext()
}

/** Lấy một media asset theo key (vd: 'logo', 'favicon', 'banner') */
export function useMediaAsset(key: string): MediaAssetRef | null {
  const config = useAppearanceContext()
  return config?.media?.[key] ?? null
}

/**
 * Lấy giá trị CSS var theo tên token key.
 * Chỉ hoạt động client-side sau khi CSS vars đã được inject vào :root.
 */
export function useColorToken(tokenKey: string): string {
  if (typeof window === 'undefined') return ''
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--color-${tokenKey}`)
    .trim()
}
