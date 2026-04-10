'use client'
import { useState, useEffect, useCallback, useRef } from 'react'
import { contentsApi } from './api'
import type {
  Post,
  PostDetail,
  PostInput,
  PostStatus,
  PlatformType,
  PostMedia,
  PostVersion,
  PostComment,
  Category,
  Tag,
  AIGeneration,
  AIGenerateInput,
  BannerLayout,
  BannerLayoutJson,
  PostTemplate,
  LayoutTemplate,
  AnalyticsSummary,
  AnalyticsDataPoint,
} from './types'

function extractError(err: unknown): string {
  const e = err as { response?: { data?: { message?: string }; status?: number } }
  if (e.response?.status === 401) return 'Phiên đăng nhập đã hết hạn'
  if (e.response?.status === 403) return 'Bạn không có quyền thực hiện thao tác này'
  return e.response?.data?.message ?? 'Đã xảy ra lỗi'
}

// ── Posts ──────────────────────────────────────────────────────

interface PostFilters {
  status?: PostStatus
  platform_type?: PlatformType
  category?: string
  search?: string
  is_ai_generated?: string
  page?: number
}

export function usePosts(filters: PostFilters = {}) {
  const [posts, setPosts] = useState<Post[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const filtersKey = JSON.stringify(filters)
  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await contentsApi.listPosts(JSON.parse(filtersKey) as PostFilters)
      setPosts(res.data.data.results)
      setCount(res.data.data.count)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [filtersKey])

  useEffect(() => { void fetch() }, [fetch])

  return { posts, count, loading, error, refetch: fetch }
}

export function usePost(id: string | null) {
  const [post, setPost] = useState<PostDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const res = await contentsApi.getPost(id)
      setPost(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { fetch() }, [fetch])

  return { post, loading, error, refetch: fetch, setPost }
}

export function useCreatePost() {
  const [loading, setLoading] = useState(false)

  const createPost = async (data: PostInput) => {
    setLoading(true)
    try {
      const res = await contentsApi.createPost(data)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  return { createPost, loading }
}

export function useUpdatePost() {
  const [loading, setLoading] = useState(false)

  const updatePost = async (id: string, data: Partial<PostInput>) => {
    setLoading(true)
    try {
      const res = await contentsApi.updatePost(id, data)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  return { updatePost, loading }
}

export function useDeletePost() {
  const [loading, setLoading] = useState(false)

  const deletePost = async (id: string) => {
    setLoading(true)
    try {
      await contentsApi.deletePost(id)
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  return { deletePost, loading }
}

export function usePostActions() {
  const [loading, setLoading] = useState(false)

  const submitReview = async (id: string) => {
    setLoading(true)
    try {
      const res = await contentsApi.submitReview(id)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  const approve = async (id: string) => {
    setLoading(true)
    try {
      const res = await contentsApi.approvePost(id)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  const reject = async (id: string, reason: string) => {
    setLoading(true)
    try {
      const res = await contentsApi.rejectPost(id, reason)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  const duplicate = async (id: string, platform_type: PlatformType) => {
    setLoading(true)
    try {
      const res = await contentsApi.duplicatePost(id, platform_type)
      return { data: res.data.data, error: null }
    } catch (err) {
      return { data: null, error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  return { submitReview, approve, reject, duplicate, loading }
}

// ── Media ─────────────────────────────────────────────────────

export function usePostMedia(postId: string | null) {
  const [media, setMedia] = useState<PostMedia[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  const fetch = useCallback(async () => {
    if (!postId) return
    setLoading(true)
    try {
      const res = await contentsApi.listMedia(postId)
      setMedia(res.data.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [postId])

  useEffect(() => { fetch() }, [fetch])

  const upload = async (file: File) => {
    if (!postId) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      await contentsApi.uploadMedia(postId, formData)
      await fetch()
    } finally {
      setUploading(false)
    }
  }

  const remove = async (mediaId: string) => {
    if (!postId) return
    setMedia((prev) => prev.filter((m) => m.id !== mediaId))
    try {
      await contentsApi.deleteMedia(postId, mediaId)
    } catch {
      await fetch()
    }
  }

  return { media, loading, uploading, upload, remove, refetch: fetch }
}

// ── Versions & Comments ───────────────────────────────────────

export function useVersions(postId: string | null) {
  const [versions, setVersions] = useState<PostVersion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!postId) {
      setVersions([])
      setLoading(false)
      return
    }

    let active = true
    setLoading(true)

    void (async () => {
      try {
        const res = await contentsApi.listVersions(postId)
        if (active) setVersions(res.data.data)
      } catch {
        // silent
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [postId])

  return { versions, loading }
}

export function useComments(postId: string | null) {
  const [comments, setComments] = useState<PostComment[]>([])
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    if (!postId) return
    setLoading(true)
    try {
      const res = await contentsApi.listComments(postId)
      setComments(res.data.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [postId])

  useEffect(() => { fetch() }, [fetch])

  const addComment = async (content: string) => {
    if (!postId) return
    try {
      const res = await contentsApi.addComment(postId, content)
      setComments((prev) => [...prev, res.data.data])
    } catch {
      // silent
    }
  }

  return { comments, loading, addComment, refetch: fetch }
}

// ── Taxonomy ──────────────────────────────────────────────────

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await contentsApi.listCategories()
      setCategories(res.data.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const create = async (data: { name: string; parent?: string | null; description?: string; order?: number }) => {
    try {
      await contentsApi.createCategory(data)
      await fetch()
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  const update = async (slug: string, data: Partial<Category>) => {
    try {
      await contentsApi.updateCategory(slug, data)
      await fetch()
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  const remove = async (slug: string) => {
    try {
      await contentsApi.deleteCategory(slug)
      await fetch()
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  return { categories, loading, create, update, remove, refetch: fetch }
}

export function useTags() {
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const res = await contentsApi.listTags()
      setTags(res.data.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const create = async (name: string) => {
    try {
      const res = await contentsApi.createTag(name)
      setTags((prev) => [...prev, res.data.data])
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  return { tags, loading, create, refetch: fetch }
}

// ── AI Generation ─────────────────────────────────────────────

export function useAIGenerate() {
  const [generation, setGeneration] = useState<AIGeneration | null>(null)
  const [loading, setLoading] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  const generate = async (data: AIGenerateInput) => {
    setLoading(true)
    setGeneration(null)
    stopPolling()
    try {
      const res = await contentsApi.generateContent(data)
      const genId = res.data.data.generation_id

      // Start polling
      intervalRef.current = setInterval(async () => {
        try {
          const pollRes = await contentsApi.pollGeneration(genId)
          const gen = pollRes.data.data
          setGeneration(gen)
          if (gen.status === 'completed' || gen.status === 'failed') {
            stopPolling()
            setLoading(false)
          }
        } catch {
          stopPolling()
          setLoading(false)
        }
      }, 2000)

      return { error: null }
    } catch (err) {
      setLoading(false)
      return { error: extractError(err) }
    }
  }

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  return { generate, generation, loading, stopPolling }
}

export function useSuggestHashtags() {
  const [loading, setLoading] = useState(false)

  const suggest = async (content: string, platform_type?: PlatformType, count?: number) => {
    setLoading(true)
    try {
      const res = await contentsApi.suggestHashtags({ content, platform_type, count })
      return { hashtags: res.data.data.hashtags, error: null }
    } catch (err) {
      return { hashtags: [], error: extractError(err) }
    } finally {
      setLoading(false)
    }
  }

  return { suggest, loading }
}

// ── Banner Layouts ────────────────────────────────────────────

export function useBannerLayouts(postId: string | null) {
  const [layouts, setLayouts] = useState<BannerLayout[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const fetch = useCallback(async () => {
    if (!postId) return
    setLoading(true)
    try {
      const res = await contentsApi.listBannerLayouts(postId)
      setLayouts(res.data.data)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [postId])

  useEffect(() => { fetch() }, [fetch])

  const generate = async (rag_instance?: string, variants?: number) => {
    if (!postId) return
    setGenerating(true)
    try {
      await contentsApi.generateBannerLayouts(postId, { rag_instance, variants })
      // Wait then refetch
      setTimeout(() => {
        fetch()
        setGenerating(false)
      }, 3000)
    } catch {
      setGenerating(false)
    }
  }

  const update = async (layoutId: string, layout_json: BannerLayoutJson) => {
    if (!postId) return
    try {
      const res = await contentsApi.updateBannerLayout(postId, layoutId, layout_json)
      setLayouts((prev) => prev.map((l) => l.id === layoutId ? res.data.data : l))
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  const approve = async (layoutId: string) => {
    if (!postId) return
    try {
      const res = await contentsApi.approveBannerLayout(postId, layoutId)
      setLayouts((prev) => prev.map((l) => l.id === layoutId ? res.data.data : l))
      return { error: null }
    } catch (err) {
      return { error: extractError(err) }
    }
  }

  return { layouts, loading, generating, generate, update, approve, refetch: fetch }
}

// ── Templates ──────────────────────────────────────────────────

export function usePostTemplates() {
  const [templates, setTemplates] = useState<PostTemplate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    contentsApi.listPostTemplates()
      .then((res) => setTemplates(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const useTemplate = async (id: string) => {
    try {
      const res = await contentsApi.usePostTemplate(id)
      return { content: res.data.data.content, error: null }
    } catch (err) {
      return { content: null, error: extractError(err) }
    }
  }

  return { templates, loading, useTemplate }
}

export function useLayoutTemplates() {
  const [templates, setTemplates] = useState<LayoutTemplate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    contentsApi.listLayoutTemplates()
      .then((res) => setTemplates(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return { templates, loading }
}

// ── Analytics ──────────────────────────────────────────────────

export function useAnalyticsSummary() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    contentsApi.getAnalyticsSummary()
      .then((res) => setSummary(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return { summary, loading }
}

export function useAnalyticsPosts(params: { from?: string; to?: string; group_by?: 'day' | 'week' | 'month' }) {
  const [dataPoints, setDataPoints] = useState<AnalyticsDataPoint[]>([])
  const [loading, setLoading] = useState(true)

  const paramsKey = JSON.stringify(params)
  useEffect(() => {
    let active = true
    setLoading(true)

    void (async () => {
      try {
        const res = await contentsApi.getAnalyticsPosts(JSON.parse(paramsKey))
        if (active) setDataPoints(res.data.data)
      } catch {
        // silent
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [paramsKey])

  return { dataPoints, loading }
}
