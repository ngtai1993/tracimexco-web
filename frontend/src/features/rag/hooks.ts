'use client'
import { useState, useEffect, useCallback } from 'react'
import { ragApi } from './api'
import type {
  RAGInstance,
  RAGInstanceInput,
  ConfigUpdateInput,
  KnowledgeBase,
  KBInput,
  Document,
  DocumentChunk,
  RAGAccessPermission,
  GrantAccessInput,
  RAGAnalytics,
  UsageLog,
  ConfigHistory,
  InstanceKBAssignment,
  InstanceSkillAssignment,
  RAGSkill,
  RAGSkillInput,
} from './types'

function extractError(err: unknown): string {
  const e = err as { response?: { data?: { message?: string }; status?: number } }
  if (e.response?.status === 401) return 'Phiên đăng nhập đã hết hạn'
  if (e.response?.status === 403) return 'Bạn không có quyền thực hiện thao tác này'
  return e.response?.data?.message ?? 'Đã xảy ra lỗi'
}

// ── Instances ──────────────────────────────────────────

export function useInstances(includeInactive = false) {
  const [instances, setInstances] = useState<RAGInstance[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listInstances(includeInactive)
      setInstances(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [includeInactive])

  useEffect(() => { fetch() }, [fetch])
  return { instances, loading, error, refetch: fetch }
}

export function useInstance(slug: string | null) {
  const [instance, setInstance] = useState<RAGInstance | null>(null)
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.getInstance(slug)
      setInstance(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { instance, loading, error, refetch: fetch }
}

export function useCreateInstance() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = useCallback(async (data: RAGInstanceInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.createInstance(data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { create, loading, error }
}

export function useUpdateInstance() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = useCallback(async (slug: string, data: Partial<RAGInstanceInput>) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.updateInstance(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { update, loading, error }
}

export function useDeleteInstance() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = useCallback(async (slug: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.deleteInstance(slug)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { remove, loading, error }
}

export function useUpdateConfig() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateConfig = useCallback(async (slug: string, data: ConfigUpdateInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.updateConfig(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { updateConfig, loading, error }
}

export function useCloneInstance() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clone = useCallback(async (slug: string, data: { new_name: string; new_slug: string }) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.cloneInstance(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { clone, loading, error }
}

// ── Instance KBs & Skills ──────────────────────────────

export function useInstanceKBs(slug: string | null) {
  const [assignments, setAssignments] = useState<InstanceKBAssignment[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listInstanceKBs(slug)
      setAssignments(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { assignments, loading, error, refetch: fetch }
}

export function useAssignKB() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const assign = useCallback(async (slug: string, data: { knowledge_base_id: string; priority: number }) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.assignKB(slug, data)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { assign, loading, error }
}

export function useInstanceSkills(slug: string | null) {
  const [assignments, setAssignments] = useState<InstanceSkillAssignment[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listInstanceSkills(slug)
      setAssignments(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { assignments, loading, error, refetch: fetch }
}

export function useAssignSkill() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const assign = useCallback(async (slug: string, data: { skill_id: string; config_override?: Record<string, unknown> }) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.assignSkill(slug, data)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { assign, loading, error }
}

export function useSkills() {
  const [skills, setSkills] = useState<RAGSkill[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listSkills()
      setSkills(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])
  return { skills, loading, error, refetch: fetch }
}

export function useCreateSkill() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = useCallback(async (data: RAGSkillInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.createSkill(data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { create, loading, error }
}

export function useUpdateSkill() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = useCallback(async (skillId: string, data: Partial<RAGSkillInput>) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.updateSkill(skillId, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { update, loading, error }
}

export function useDeleteSkill() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = useCallback(async (skillId: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.deleteSkill(skillId)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { remove, loading, error }
}

// ── Knowledge Bases ────────────────────────────────────

export function useKnowledgeBases(includeInactive = false) {
  const [kbs, setKBs] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listKBs(includeInactive)
      setKBs(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [includeInactive])

  useEffect(() => { fetch() }, [fetch])
  return { kbs, loading, error, refetch: fetch }
}

export function useKnowledgeBase(slug: string | null) {
  const [kb, setKB] = useState<KnowledgeBase | null>(null)
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.getKB(slug)
      setKB(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { kb, loading, error, refetch: fetch }
}

export function useCreateKB() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = useCallback(async (data: KBInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.createKB(data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { create, loading, error }
}

export function useDeleteKB() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = useCallback(async (slug: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.deleteKB(slug)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { remove, loading, error }
}

// ── Documents ──────────────────────────────────────────

export function useDocuments(kbSlug: string | null, isImage?: boolean) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(!!kbSlug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!kbSlug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listDocuments(kbSlug, isImage)
      setDocuments(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [kbSlug, isImage])

  useEffect(() => { fetch() }, [fetch])
  return { documents, loading, error, refetch: fetch }
}

export function useUploadDocument() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const upload = useCallback(async (kbSlug: string, formData: FormData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.uploadDocument(kbSlug, formData)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { upload, loading, error }
}

export function useAddTextDocument() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const add = useCallback(async (kbSlug: string, data: { title: string; content_text: string; description?: string }) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.addTextDocument(kbSlug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { add, loading, error }
}

export function useAddURLDocument() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const add = useCallback(async (kbSlug: string, data: { title: string; source_url: string; description?: string }) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.addURLDocument(kbSlug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { add, loading, error }
}

export function useDeleteDocument() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = useCallback(async (docId: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.deleteDocument(docId)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { remove, loading, error }
}

export function useDocumentChunks(docId: string | null) {
  const [chunks, setChunks] = useState<DocumentChunk[]>([])
  const [loading, setLoading] = useState(!!docId)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!docId) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listChunks(docId)
      setChunks(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [docId])

  useEffect(() => { fetch() }, [fetch])
  return { chunks, loading, error, refetch: fetch }
}

export function useBuildGraph() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const build = useCallback(async (kbSlug: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.buildGraph(kbSlug)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { build, loading, error }
}

// ── Access ─────────────────────────────────────────────

export function useAccess(slug: string | null) {
  const [permissions, setPermissions] = useState<RAGAccessPermission[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listAccess(slug)
      setPermissions(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { permissions, loading, error, refetch: fetch }
}

export function useGrantAccess() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const grant = useCallback(async (slug: string, data: GrantAccessInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.grantAccess(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { grant, loading, error }
}

export function useRevokeAccess() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const revoke = useCallback(async (slug: string, permId: string) => {
    setLoading(true)
    setError(null)
    try {
      await ragApi.revokeAccess(slug, permId)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { revoke, loading, error }
}

// ── Analytics ──────────────────────────────────────────

export function useAnalytics(slug: string | null, days = 7) {
  const [analytics, setAnalytics] = useState<RAGAnalytics | null>(null)
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.getAnalytics(slug, days)
      setAnalytics(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug, days])

  useEffect(() => { fetch() }, [fetch])
  return { analytics, loading, error, refetch: fetch }
}

export function useUsageLogs(slug: string | null, limit = 50) {
  const [logs, setLogs] = useState<UsageLog[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listUsageLogs(slug, limit)
      setLogs(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug, limit])

  useEffect(() => { fetch() }, [fetch])
  return { logs, loading, error, refetch: fetch }
}

export function useConfigHistory(slug: string | null, limit = 20) {
  const [history, setHistory] = useState<ConfigHistory[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await ragApi.listConfigHistory(slug, limit)
      setHistory(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug, limit])

  useEffect(() => { fetch() }, [fetch])
  return { history, loading, error, refetch: fetch }
}
