'use client'
import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { ChatSidebar } from './ChatSidebar'
import { ChatWindow } from './ChatWindow'
import { ChatInput } from './ChatInput'
import { QuotaIndicator } from './QuotaIndicator'
import { useConversations, useMessages, useSendQuery } from '../hooks'
import type { RAGMessage } from '../types'

interface ChatLayoutProps {
  instanceSlug: string
  instanceName?: string
  conversationId?: string | null
}

export function ChatLayout({ instanceSlug, instanceName, conversationId: initialConvId }: ChatLayoutProps) {
  const router = useRouter()
  const [activeConvId, setActiveConvId] = useState<string | null>(initialConvId ?? null)
  const { conversations, refetch: refetchConvs } = useConversations(instanceSlug)
  const { messages, setMessages } = useMessages(instanceSlug, activeConvId)
  const { send, loading: sending } = useSendQuery()

  const handleSelect = useCallback((id: string) => {
    setActiveConvId(id)
    router.push(`/dashboard/chat/${instanceSlug}/${id}`)
  }, [instanceSlug, router])

  const handleNew = useCallback(() => {
    setActiveConvId(null)
    setMessages([])
    router.push(`/dashboard/chat/${instanceSlug}`)
  }, [instanceSlug, router, setMessages])

  const handleSend = useCallback(async (query: string) => {
    // Optimistic user message
    const tempUserMsg: RAGMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: query,
      sources: [],
      images: [],
      skills_used: [],
      metadata: { tokens_in: 0, tokens_out: 0, latency_ms: 0, retrieval_strategy: '', model: '' },
      feedback: null,
      feedback_comment: '',
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUserMsg])

    const result = await send(instanceSlug, {
      query,
      conversation_id: activeConvId,
    })

    if (result) {
      // Construct assistant message from response
      const assistantMsg: RAGMessage = {
        id: result.message_id,
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
        images: result.images,
        skills_used: [],
        metadata: result.metadata,
        feedback: null,
        feedback_comment: '',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMsg])

      // Update conversation ID if new
      if (!activeConvId && result.conversation_id) {
        setActiveConvId(result.conversation_id)
        router.push(`/dashboard/chat/${instanceSlug}/${result.conversation_id}`)
      }
      refetchConvs()
    }
  }, [instanceSlug, activeConvId, send, setMessages, refetchConvs, router])

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <ChatSidebar
        conversations={conversations}
        selectedId={activeConvId}
        onSelect={handleSelect}
        onNew={handleNew}
        instanceSlug={instanceSlug}
        onDeleted={() => {
          handleNew()
          refetchConvs()
        }}
      />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
          <h2 className="text-sm font-medium text-fg">
            {instanceName ?? instanceSlug}
          </h2>
          <QuotaIndicator instanceSlug={instanceSlug} />
        </div>

        {/* Messages */}
        <ChatWindow
          messages={messages}
          loading={sending}
          instanceName={instanceName}
        />

        {/* Input */}
        <ChatInput onSend={handleSend} loading={sending} />
      </div>
    </div>
  )
}
