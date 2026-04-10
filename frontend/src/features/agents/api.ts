import { apiClient } from '@/lib/api'
import type { ApiResponse } from '@/types/api'
import type {
  AgentProvider,
  AgentProviderInput,
  AgentAPIKey,
  AgentAPIKeyInput,
  AgentAPIKeyUpdate,
  AgentConfig,
  AgentConfigInput,
} from './types'

const BASE = '/api/v1/agents/providers'

export const agentApi = {
  // ── Providers ────────────────────────────────────────
  listProviders: (includeInactive = false) =>
    apiClient.get<ApiResponse<AgentProvider[]>>(`${BASE}/`, {
      params: { include_inactive: includeInactive },
    }),

  getProvider: (slug: string) =>
    apiClient.get<ApiResponse<AgentProvider>>(`${BASE}/${slug}/`),

  createProvider: (data: AgentProviderInput) =>
    apiClient.post<ApiResponse<AgentProvider>>(`${BASE}/`, data),

  updateProvider: (slug: string, data: Partial<AgentProviderInput>) =>
    apiClient.patch<ApiResponse<AgentProvider>>(`${BASE}/${slug}/`, data),

  deleteProvider: (slug: string) =>
    apiClient.delete(`${BASE}/${slug}/`),

  // ── Keys ─────────────────────────────────────────────
  listKeys: (slug: string) =>
    apiClient.get<ApiResponse<AgentAPIKey[]>>(`${BASE}/${slug}/keys/`),

  createKey: (slug: string, data: AgentAPIKeyInput) =>
    apiClient.post<ApiResponse<AgentAPIKey>>(`${BASE}/${slug}/keys/`, data),

  updateKey: (slug: string, keyId: string, data: AgentAPIKeyUpdate) =>
    apiClient.patch<ApiResponse<AgentAPIKey>>(`${BASE}/${slug}/keys/${keyId}/`, data),

  deleteKey: (slug: string, keyId: string) =>
    apiClient.delete(`${BASE}/${slug}/keys/${keyId}/`),

  // ── Configs ──────────────────────────────────────────
  listConfigs: (slug: string) =>
    apiClient.get<ApiResponse<AgentConfig[]>>(`${BASE}/${slug}/configs/`),

  createConfig: (slug: string, data: AgentConfigInput) =>
    apiClient.post<ApiResponse<AgentConfig>>(`${BASE}/${slug}/configs/`, data),

  updateConfig: (slug: string, configId: string, data: Partial<AgentConfigInput>) =>
    apiClient.patch<ApiResponse<AgentConfig>>(`${BASE}/${slug}/configs/${configId}/`, data),

  deleteConfig: (slug: string, configId: string) =>
    apiClient.delete(`${BASE}/${slug}/configs/${configId}/`),
}
