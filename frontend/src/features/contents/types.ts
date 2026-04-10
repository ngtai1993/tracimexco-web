// ── Post Status & Platform ────────────────────────────────────

export type PostStatus = 'draft' | 'review' | 'approved' | 'scheduled' | 'published' | 'archived'
export type PlatformType = 'facebook' | 'zalo' | 'tiktok' | 'linkedin' | 'twitter' | 'custom'
export type MediaType = 'image' | 'video' | 'file'
export type GenerationStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type GenerationType = 'full_post' | 'hashtags' | 'summary' | 'caption' | 'translation' | 'improvement' | 'ab_variant'

// ── Post ──────────────────────────────────────────────────────

export interface Post {
  id: string
  title: string
  status: PostStatus
  platform_type: PlatformType
  author_name: string
  category_name: string | null
  tags: { id: string; name: string }[]
  is_ai_generated: boolean
  created_at: string
  updated_at: string
}

export interface PostDetail extends Post {
  content: string
  hashtags: string[]
  category: { id: string; name: string; slug: string } | null
  media: PostMedia[]
}

export interface PostInput {
  title: string
  content: string
  hashtags?: string[]
  platform_type: PlatformType
  category?: string | null
  tags?: string[]
  rag_instance?: string | null
  is_ai_generated?: boolean
}

// ── Media ─────────────────────────────────────────────────────

export interface PostMedia {
  id: string
  media_type: MediaType
  file: string
  file_url: string | null
  caption: string
  order: number
  created_at: string
}

// ── Version ───────────────────────────────────────────────────

export interface PostVersion {
  id: string
  version_number: number
  title: string
  content: string
  changed_by_name: string | null
  created_at: string
}

// ── Comment ───────────────────────────────────────────────────

export interface PostComment {
  id: string
  author_name: string
  content: string
  created_at: string
}

// ── Category ──────────────────────────────────────────────────

export interface Category {
  id: string
  name: string
  slug: string
  parent: string | null
  description: string
  order: number
}

// ── Tag ───────────────────────────────────────────────────────

export interface Tag {
  id: string
  name: string
  slug: string
}

// ── AI Generation ─────────────────────────────────────────────

export interface AIGeneration {
  id: string
  generation_type: GenerationType
  prompt: string
  status: GenerationStatus
  result_content: string
  result_variants: string[]
  error_message: string
  created_at: string
}

export interface AIGenerateInput {
  rag_instance: string
  prompt: string
  platform_type?: PlatformType
  variants?: number
  language?: 'vi' | 'en'
}

// ── Banner Layout ─────────────────────────────────────────────

export interface BannerLayoutJson {
  title?: string
  tagline?: string
  background?: { type: 'color' | 'gradient' | 'image'; value: string }
  title_position?: 'top-center' | 'center' | 'bottom-left'
  font_family?: string
  accent_color?: string
  logo_placement?: 'top-left' | 'top-right' | 'none'
  layout_style?: 'bold' | 'minimal' | 'elegant' | 'playful'
}

export interface BannerLayout {
  id: string
  variant_index: number
  layout_json: BannerLayoutJson
  is_approved: boolean
  approved_by?: string | null
}

// ── Templates ─────────────────────────────────────────────────

export interface PostTemplate {
  id: string
  name: string
  platform_type: PlatformType
  content_template: string
  category: string | null
  is_active: boolean
}

export interface LayoutTemplate {
  id: string
  name: string
  platform_type: PlatformType | ''
  layout_json: BannerLayoutJson
  is_active: boolean
}

// ── Analytics ─────────────────────────────────────────────────

export interface AnalyticsSummary {
  total_posts: number
  by_status: Record<string, number>
  by_platform: Record<string, number>
  ai_generated_count: number
  publish_success_rate: number | null
}

export interface AnalyticsDataPoint {
  period: string
  count: number
}
