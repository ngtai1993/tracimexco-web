// ── Provider ──────────────────────────────
export interface AgentProvider {
  id: string
  name: string
  slug: string
  description: string
  website_url: string
  is_active: boolean
  keys_count: number
  active_keys_count: number
  created_at: string
  updated_at: string
}

export interface AgentProviderInput {
  name: string
  slug: string
  description?: string
  website_url?: string
  is_active?: boolean
}

// ── API Key ───────────────────────────────
export interface AgentAPIKey {
  id: string
  name: string
  key_preview: string
  is_active: boolean
  priority: number
  last_used_at: string | null
  expires_at: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface AgentAPIKeyInput {
  name: string
  raw_key: string
  priority?: number
  expires_at?: string | null
}

export interface AgentAPIKeyUpdate {
  name?: string
  priority?: number
  is_active?: boolean
  expires_at?: string | null
}

// ── Config ────────────────────────────────
export interface AgentConfig {
  id: string
  name: string
  model_name: string
  config_json: Record<string, unknown>
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AgentConfigInput {
  name: string
  model_name: string
  config_json?: Record<string, unknown>
  is_default?: boolean
  is_active?: boolean
}
