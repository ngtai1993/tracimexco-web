// ── Conversation ──────────────────────────
export interface RAGConversation {
  id: string
  title: string
  message_count: number
  last_message: string | null
  created_at: string
  updated_at: string
}

export interface RAGMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sources: Source[]
  images: ImageResult[]
  skills_used: string[]
  metadata: MessageMetadata
  feedback: 'positive' | 'negative' | null
  feedback_comment: string
  created_at: string
}

export interface Source {
  chunk_id: string
  document_title: string
  content: string
  score: number
}

export interface ImageResult {
  id: string
  url: string
  caption: string
  score: number
}

export interface MessageMetadata {
  tokens_in: number
  tokens_out: number
  latency_ms: number
  retrieval_strategy: string
  model: string
}

// ── Chat Request/Response ─────────────────
export interface ChatQueryInput {
  query: string
  conversation_id?: string | null
}

export interface ChatResponse {
  answer: string
  sources: Source[]
  images: ImageResult[]
  conversation_id: string
  message_id: string
  metadata: MessageMetadata
}

export interface FeedbackInput {
  feedback: 'positive' | 'negative'
  comment?: string
}

export interface MyAccess {
  has_access: boolean
  access_level?: string
  daily_queries_used?: number
  daily_query_limit?: number
  monthly_tokens_used?: number
  monthly_token_limit?: number
  note?: string
}
