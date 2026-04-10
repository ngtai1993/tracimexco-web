import { apiClient } from '@/lib/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import type {
  Post,
  PostDetail,
  PostInput,
  PostMedia,
  PostVersion,
  PostComment,
  PostStatus,
  PlatformType,
  GenerationStatus,
  AIGeneration,
  AIGenerateInput,
  BannerLayout,
  BannerLayoutJson,
  Category,
  Tag,
  PostTemplate,
  LayoutTemplate,
  AnalyticsSummary,
  AnalyticsDataPoint,
} from './types'

const BASE = '/api/v1/contents'

export const contentsApi = {
  // ── Posts ──────────────────────────────────────────

  listPosts: (params?: {
    status?: PostStatus
    platform_type?: PlatformType
    category?: string
    search?: string
    is_ai_generated?: string
    page?: number
  }) => apiClient.get<PaginatedResponse<Post>>(`${BASE}/posts/`, { params }),

  getPost: (id: string) =>
    apiClient.get<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/`),

  createPost: (data: PostInput) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/`, data),

  updatePost: (id: string, data: Partial<PostInput>) =>
    apiClient.patch<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/`, data),

  deletePost: (id: string) =>
    apiClient.delete(`${BASE}/posts/${id}/`),

  duplicatePost: (id: string, platform_type: PlatformType) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/duplicate/`, { platform_type }),

  submitReview: (id: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/submit-review/`),

  approvePost: (id: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/approve/`),

  rejectPost: (id: string, reason: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/reject/`, { reason }),

  // ── Media ──────────────────────────────────────────

  listMedia: (postId: string) =>
    apiClient.get<ApiResponse<PostMedia[]>>(`${BASE}/posts/${postId}/media/`),

  uploadMedia: (postId: string, formData: FormData) =>
    apiClient.post<ApiResponse<PostMedia>>(`${BASE}/posts/${postId}/media/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  deleteMedia: (postId: string, mediaId: string) =>
    apiClient.delete(`${BASE}/posts/${postId}/media/${mediaId}/`),

  // ── Versions & Comments ────────────────────────────

  listVersions: (postId: string) =>
    apiClient.get<ApiResponse<PostVersion[]>>(`${BASE}/posts/${postId}/versions/`),

  listComments: (postId: string) =>
    apiClient.get<ApiResponse<PostComment[]>>(`${BASE}/posts/${postId}/comments/`),

  addComment: (postId: string, content: string) =>
    apiClient.post<ApiResponse<PostComment>>(`${BASE}/posts/${postId}/comments/`, { content }),

  // ── Taxonomy ──────────────────────────────────────

  listCategories: () =>
    apiClient.get<ApiResponse<Category[]>>(`${BASE}/categories/`),

  createCategory: (data: { name: string; slug?: string; parent?: string | null; description?: string; order?: number }) =>
    apiClient.post<ApiResponse<Category>>(`${BASE}/categories/`, data),

  updateCategory: (slug: string, data: Partial<Category>) =>
    apiClient.patch<ApiResponse<Category>>(`${BASE}/categories/${slug}/`, data),

  deleteCategory: (slug: string) =>
    apiClient.delete(`${BASE}/categories/${slug}/`),

  listTags: () =>
    apiClient.get<ApiResponse<Tag[]>>(`${BASE}/tags/`),

  createTag: (name: string) =>
    apiClient.post<ApiResponse<Tag>>(`${BASE}/tags/`, { name }),

  // ── AI Generation ──────────────────────────────────

  generateContent: (data: AIGenerateInput) =>
    apiClient.post<ApiResponse<{ generation_id: string; status: GenerationStatus }>>(`${BASE}/ai/generate/`, data),

  pollGeneration: (id: string) =>
    apiClient.get<ApiResponse<AIGeneration>>(`${BASE}/ai/generations/${id}/`),

  suggestHashtags: (data: { content: string; platform_type?: PlatformType; count?: number }) =>
    apiClient.post<ApiResponse<{ hashtags: string[] }>>(`${BASE}/ai/suggest-hashtags/`, data),

  summarize: (data: { content: string; platform_type?: PlatformType; max_length?: number }) =>
    apiClient.post<ApiResponse<{ summary: string }>>(`${BASE}/ai/summarize/`, data),

  translate: (data: { content: string; target_language: string }) =>
    apiClient.post<ApiResponse<{ translated: string }>>(`${BASE}/ai/translate/`, data),

  improve: (data: { content: string; platform_type?: PlatformType; tone?: string }) =>
    apiClient.post<ApiResponse<{ improved: string }>>(`${BASE}/ai/improve/`, data),

  generateCaption: (data: { context: string; platform_type?: PlatformType }) =>
    apiClient.post<ApiResponse<{ caption: string }>>(`${BASE}/ai/generate-caption/`, data),

  // ── Banner Layouts ─────────────────────────────────

  listBannerLayouts: (postId: string) =>
    apiClient.get<ApiResponse<BannerLayout[]>>(`${BASE}/posts/${postId}/banner-layouts/`),

  generateBannerLayouts: (postId: string, data: { rag_instance?: string; variants?: number }) =>
    apiClient.post(`${BASE}/posts/${postId}/banner-layouts/generate/`, data),

  updateBannerLayout: (postId: string, layoutId: string, layout_json: BannerLayoutJson) =>
    apiClient.patch<ApiResponse<BannerLayout>>(`${BASE}/posts/${postId}/banner-layouts/${layoutId}/`, { layout_json }),

  approveBannerLayout: (postId: string, layoutId: string) =>
    apiClient.post<ApiResponse<BannerLayout>>(`${BASE}/posts/${postId}/banner-layouts/${layoutId}/approve/`),

  // ── Templates ─────────────────────────────────────

  listPostTemplates: () =>
    apiClient.get<ApiResponse<PostTemplate[]>>(`${BASE}/templates/`),

  usePostTemplate: (id: string) =>
    apiClient.post<ApiResponse<{ content: string }>>(`${BASE}/templates/${id}/use/`),

  listLayoutTemplates: () =>
    apiClient.get<ApiResponse<LayoutTemplate[]>>(`${BASE}/layout-templates/`),

  // ── Analytics ─────────────────────────────────────

  getAnalyticsSummary: () =>
    apiClient.get<ApiResponse<AnalyticsSummary>>(`${BASE}/analytics/summary/`),

  getAnalyticsPosts: (params: { from?: string; to?: string; group_by?: 'day' | 'week' | 'month' }) =>
    apiClient.get<ApiResponse<AnalyticsDataPoint[]>>(`${BASE}/analytics/posts/`, { params }),

  getPublishHistory: (params?: { platform?: string; status?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<Record<string, unknown>>>(`${BASE}/analytics/publish-history/`, { params }),
}
