import { apiClient } from '@/lib/api'
import type { ApiResponse } from '@/types/api'
import type {
  RAGConversation,
  RAGMessage,
  ChatQueryInput,
  ChatResponse,
  FeedbackInput,
  MyAccess,
} from './types'

const INST = '/api/v1/graph-rag/instances'
const MSG = '/api/v1/graph-rag/messages'

export const chatApi = {
  // Chat
  sendQuery: (slug: string, data: ChatQueryInput) =>
    apiClient.post<ApiResponse<ChatResponse>>(`${INST}/${slug}/chat/`, data),

  // Conversations
  listConversations: (slug: string) =>
    apiClient.get<ApiResponse<RAGConversation[]>>(`${INST}/${slug}/conversations/`),
  getConversation: (slug: string, conversationId: string) =>
    apiClient.get<ApiResponse<RAGMessage[]>>(`${INST}/${slug}/conversations/${conversationId}/`),
  deleteConversation: (slug: string, conversationId: string) =>
    apiClient.delete(`${INST}/${slug}/conversations/${conversationId}/`),

  // Feedback
  submitFeedback: (messageId: string, data: FeedbackInput) =>
    apiClient.post(`${MSG}/${messageId}/feedback/`, data),

  // Access check
  getMyAccess: (slug: string) =>
    apiClient.get<ApiResponse<MyAccess>>(`${INST}/${slug}/my-access/`),
}
