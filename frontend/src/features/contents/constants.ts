import type { PostStatus, PlatformType } from './types'

export const STATUS_LABELS: Record<PostStatus, string> = {
  draft: 'Nháp',
  review: 'Chờ duyệt',
  approved: 'Đã duyệt',
  scheduled: 'Đã lên lịch',
  published: 'Đã đăng',
  archived: 'Lưu trữ',
}

export const STATUS_COLORS: Record<PostStatus, string> = {
  draft: 'neutral',
  review: 'warning',
  approved: 'info',
  scheduled: 'info',
  published: 'success',
  archived: 'danger',
}

export const PLATFORM_LABELS: Record<PlatformType, string> = {
  facebook: 'Facebook',
  zalo: 'Zalo',
  tiktok: 'TikTok',
  linkedin: 'LinkedIn',
  twitter: 'Twitter/X',
  custom: 'Custom',
}

export const PLATFORM_ICONS: Record<PlatformType, string> = {
  facebook: '📘',
  zalo: '💬',
  tiktok: '🎵',
  linkedin: '💼',
  twitter: '🐦',
  custom: '🌐',
}

export const PLATFORM_CHAR_LIMITS: Record<PlatformType, number> = {
  facebook: 63206,
  zalo: 5000,
  tiktok: 2200,
  linkedin: 3000,
  twitter: 280,
  custom: Infinity,
}

export const PLATFORM_OPTIONS = Object.entries(PLATFORM_LABELS).map(([value, label]) => ({
  value,
  label,
}))

export const STATUS_OPTIONS = Object.entries(STATUS_LABELS).map(([value, label]) => ({
  value,
  label,
}))

export const ALL_STATUSES: PostStatus[] = ['draft', 'review', 'approved', 'scheduled', 'published', 'archived']
