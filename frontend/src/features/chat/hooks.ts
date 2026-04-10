'use client'
import { useState, useEffect, useCallback } from 'react'
import { chatApi } from './api'
import type {
  RAGConversation,
  RAGMessage,
  ChatQueryInput,
  FeedbackInput,
  MyAccess,
} from './types'

function extractError(err: unknown): string {
  const e = err as { response?: { data?: { message?: string }; status?: number } }
  if (e.response?.status === 401) return 'Phiên đăng nhập đã hết hạn'
  if (e.response?.status === 403) return 'Bạn không có quyền thực hiện thao tác này'
  return e.response?.data?.message ?? 'Đã xảy ra lỗi'
}

export function useConversations(slug: string | null) {
  const [conversations, setConversations] = useState<RAGConversation[]>([])
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await chatApi.listConversations(slug)
      setConversations(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { conversations, loading, error, refetch: fetch }
}

export function useMessages(slug: string | null, conversationId: string | null) {
  const [messages, setMessages] = useState<RAGMessage[]>([])
  const [loading, setLoading] = useState(!!(slug && conversationId))
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug || !conversationId) return
    setLoading(true)
    setError(null)
    try {
      const res = await chatApi.getConversation(slug, conversationId)
      setMessages(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug, conversationId])

  useEffect(() => { fetch() }, [fetch])
  return { messages, setMessages, loading, error, refetch: fetch }
}

export function useSendQuery() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = useCallback(async (slug: string, data: ChatQueryInput) => {
    setLoading(true)
    setError(null)
    try {
      const res = await chatApi.sendQuery(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { send, loading, error }
}

export function useDeleteConversation() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = useCallback(async (slug: string, conversationId: string) => {
    setLoading(true)
    setError(null)
    try {
      await chatApi.deleteConversation(slug, conversationId)
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

export function useSubmitFeedback() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = useCallback(async (messageId: string, data: FeedbackInput) => {
    setLoading(true)
    setError(null)
    try {
      await chatApi.submitFeedback(messageId, data)
      return true
    } catch (err) {
      setError(extractError(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { submit, loading, error }
}

export function useMyAccess(slug: string | null) {
  const [access, setAccess] = useState<MyAccess | null>(null)
  const [loading, setLoading] = useState(!!slug)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!slug) return
    setLoading(true)
    setError(null)
    try {
      const res = await chatApi.getMyAccess(slug)
      setAccess(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [slug])

  useEffect(() => { fetch() }, [fetch])
  return { access, loading, error, refetch: fetch }
}
