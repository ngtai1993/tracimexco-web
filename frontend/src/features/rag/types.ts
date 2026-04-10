// ── RAG Instance ──────────────────────────
export interface RAGInstance {
  id: string
  name: string
  slug: string
  description: string
  purpose: string
  system_prompt: string
  provider_name: string
  agent_config_name: string | null
  retrieval_config: RetrievalConfig
  generation_config: GenerationConfig
  is_active: boolean
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface RetrievalConfig {
  search_strategy: 'hybrid' | 'vector' | 'keyword' | 'graph'
  top_k_vector: number
  top_k_graph: number
  top_k_final: number
  similarity_threshold: number
  graph_depth: number
  embedding_model: string
  images_enabled: boolean
  reranking_enabled: boolean
  query_decomposition: boolean
}

export interface GenerationConfig {
  temperature: number
  max_tokens: number
  response_format: 'markdown' | 'text'
  language: 'vi' | 'en'
  tone: 'professional' | 'casual' | 'technical'
  include_sources: boolean
  stream: boolean
}

export interface RAGInstanceInput {
  name: string
  slug: string
  description?: string
  purpose?: string
  system_prompt: string
  provider_id: string
  agent_config_id?: string | null
  retrieval_config?: Partial<RetrievalConfig>
  generation_config?: Partial<GenerationConfig>
  is_public?: boolean
}

export interface ConfigUpdateInput {
  config_type: 'retrieval' | 'generation'
  config: Record<string, unknown>
  reason?: string
}

// ── Knowledge Base ────────────────────────
export interface KnowledgeBase {
  id: string
  name: string
  slug: string
  description: string
  chunk_strategy: 'fixed' | 'recursive' | 'semantic'
  chunk_size: number
  chunk_overlap: number
  embedding_model: string
  embedding_dimensions: number
  document_count: number
  image_count: number
  total_chunks: number
  is_active: boolean
  graph_status: 'not_built' | 'building' | 'ready' | 'failed' | null
  created_at: string
  updated_at: string
}

export interface KBInput {
  name: string
  slug: string
  description?: string
  chunk_strategy?: string
  chunk_size?: number
  chunk_overlap?: number
  embedding_model?: string
}

// ── Document ──────────────────────────────
export interface Document {
  id: string
  title: string
  description: string
  source_type: 'file' | 'text' | 'url'
  is_image: boolean
  image_caption: string
  image_tags: string[]
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_error: string
  chunk_count: number
  token_count: number
  kb_name: string
  metadata: Record<string, unknown>
  processed_at: string | null
  created_at: string
  updated_at: string
}

export interface DocumentChunk {
  id: string
  chunk_index: number
  content: string
  token_count: number
  is_image_chunk: boolean
  metadata: Record<string, unknown>
  created_at: string
}

// ── Access ────────────────────────────────
export interface RAGAccessPermission {
  id: string
  user_email: string
  access_level: 'use' | 'manage'
  daily_query_limit: number
  monthly_token_limit: number
  expires_at: string | null
  granted_by_email: string | null
  created_at: string
}

export interface GrantAccessInput {
  user_id: string
  access_level?: string
  daily_query_limit?: number
  monthly_token_limit?: number
  expires_at?: string | null
}

// ── Analytics ─────────────────────────────
export interface RAGAnalytics {
  total_queries: number
  unique_users: number
  total_tokens_in: number
  total_tokens_out: number
  avg_latency_ms: number
  total_images: number
}

export interface UsageLog {
  id: string
  query: string
  retrieval_strategy: string
  tokens_in: number
  tokens_out: number
  latency_ms: number
  sources_count: number
  images_returned: number
  created_at: string
}

export interface ConfigHistory {
  id: string
  config_type: 'retrieval' | 'generation'
  old_value: Record<string, unknown>
  new_value: Record<string, unknown>
  reason: string
  changed_by_email: string | null
  created_at: string
}

// ── Instance assignments ──────────────────
export interface InstanceKBAssignment {
  priority: number
  knowledge_base: KnowledgeBase
}

export interface InstanceSkillAssignment {
  is_enabled: boolean
  config_override: Record<string, unknown>
  skill: RAGSkill
}

export interface RAGSkill {
  id: string
  name: string
  slug: string
  description: string
  skill_type: string
  is_active: boolean
  created_at: string
}
