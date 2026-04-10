import { apiClient } from '@/lib/api'
import type { ApiResponse } from '@/types/api'
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

const INST = '/api/v1/graph-rag/instances'
const KB = '/api/v1/graph-rag/knowledge-bases'
const DOC = '/api/v1/graph-rag/documents'
const SKILL = '/api/v1/graph-rag/skills'

export const ragApi = {
  // ── Instances ────────────────────────────────────────
  listInstances: (includeInactive = false) =>
    apiClient.get<ApiResponse<RAGInstance[]>>(`${INST}/`, {
      params: { include_inactive: includeInactive },
    }),
  getInstance: (slug: string) =>
    apiClient.get<ApiResponse<RAGInstance>>(`${INST}/${slug}/`),
  createInstance: (data: RAGInstanceInput) =>
    apiClient.post<ApiResponse<RAGInstance>>(`${INST}/`, data),
  updateInstance: (slug: string, data: Partial<RAGInstanceInput>) =>
    apiClient.patch<ApiResponse<RAGInstance>>(`${INST}/${slug}/`, data),
  deleteInstance: (slug: string) =>
    apiClient.delete(`${INST}/${slug}/`),
  updateConfig: (slug: string, data: ConfigUpdateInput) =>
    apiClient.patch<ApiResponse<RAGInstance>>(`${INST}/${slug}/config/`, data),
  cloneInstance: (slug: string, data: { new_name: string; new_slug: string }) =>
    apiClient.post<ApiResponse<RAGInstance>>(`${INST}/${slug}/clone/`, data),

  // ── Instance KBs & Skills ───────────────────────────
  listInstanceKBs: (slug: string) =>
    apiClient.get<ApiResponse<InstanceKBAssignment[]>>(`${INST}/${slug}/knowledge-bases/`),
  assignKB: (slug: string, data: { knowledge_base_id: string; priority: number }) =>
    apiClient.post(`${INST}/${slug}/knowledge-bases/`, data),
  removeKBFromInstance: (slug: string, kbId: string) =>
    apiClient.delete(`${INST}/${slug}/knowledge-bases/${kbId}/`),
  listInstanceSkills: (slug: string) =>
    apiClient.get<ApiResponse<InstanceSkillAssignment[]>>(`${INST}/${slug}/skills/`),
  assignSkill: (slug: string, data: { skill_id: string; config_override?: Record<string, unknown> }) =>
    apiClient.post(`${INST}/${slug}/skills/`, data),
  removeSkillFromInstance: (slug: string, skillId: string) =>
    apiClient.delete(`${INST}/${slug}/skills/${skillId}/`),
  listSkills: () =>
    apiClient.get<ApiResponse<RAGSkill[]>>(`${SKILL}/`),
  createSkill: (data: RAGSkillInput) =>
    apiClient.post<ApiResponse<RAGSkill>>(`${SKILL}/`, data),
  updateSkill: (skillId: string, data: Partial<RAGSkillInput>) =>
    apiClient.patch<ApiResponse<RAGSkill>>(`${SKILL}/${skillId}/`, data),
  deleteSkill: (skillId: string) =>
    apiClient.delete(`${SKILL}/${skillId}/`),

  // ── Knowledge Bases ─────────────────────────────────
  listKBs: (includeInactive = false) =>
    apiClient.get<ApiResponse<KnowledgeBase[]>>(`${KB}/`, {
      params: { include_inactive: includeInactive },
    }),
  getKB: (slug: string) =>
    apiClient.get<ApiResponse<KnowledgeBase>>(`${KB}/${slug}/`),
  createKB: (data: KBInput) =>
    apiClient.post<ApiResponse<KnowledgeBase>>(`${KB}/`, data),
  deleteKB: (slug: string) =>
    apiClient.delete(`${KB}/${slug}/`),

  // ── Documents ───────────────────────────────────────
  listDocuments: (kbSlug: string, isImage?: boolean) =>
    apiClient.get<ApiResponse<Document[]>>(`${KB}/${kbSlug}/documents/`, {
      params: isImage !== undefined ? { is_image: isImage } : {},
    }),
  uploadDocument: (kbSlug: string, formData: FormData) =>
    apiClient.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  addTextDocument: (kbSlug: string, data: { title: string; content_text: string; description?: string }) =>
    apiClient.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/text/`, data),
  addURLDocument: (kbSlug: string, data: { title: string; source_url: string; description?: string }) =>
    apiClient.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/url/`, data),
  getDocument: (docId: string) =>
    apiClient.get<ApiResponse<Document>>(`${DOC}/${docId}/`),
  deleteDocument: (docId: string) =>
    apiClient.delete(`${DOC}/${docId}/`),
  listChunks: (docId: string) =>
    apiClient.get<ApiResponse<DocumentChunk[]>>(`${DOC}/${docId}/chunks/`),
  buildGraph: (kbSlug: string) =>
    apiClient.post(`${KB}/${kbSlug}/graph/build/`),

  // ── Access ──────────────────────────────────────────
  listAccess: (slug: string) =>
    apiClient.get<ApiResponse<RAGAccessPermission[]>>(`${INST}/${slug}/access/`),
  grantAccess: (slug: string, data: GrantAccessInput) =>
    apiClient.post<ApiResponse<RAGAccessPermission>>(`${INST}/${slug}/access/`, data),
  revokeAccess: (slug: string, permId: string) =>
    apiClient.delete(`${INST}/${slug}/access/${permId}/`),

  // ── Analytics ───────────────────────────────────────
  getAnalytics: (slug: string, days = 7) =>
    apiClient.get<ApiResponse<RAGAnalytics>>(`${INST}/${slug}/analytics/`, {
      params: { days },
    }),
  listUsageLogs: (slug: string, limit = 50) =>
    apiClient.get<ApiResponse<UsageLog[]>>(`${INST}/${slug}/usage-logs/`, {
      params: { limit },
    }),
  listConfigHistory: (slug: string, limit = 20) =>
    apiClient.get<ApiResponse<ConfigHistory[]>>(`${INST}/${slug}/config-history/`, {
      params: { limit },
    }),
}
