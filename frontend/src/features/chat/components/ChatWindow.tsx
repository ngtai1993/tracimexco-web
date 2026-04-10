'use client'
import { useRef, useEffect } from 'react'
import { ChatMessage } from './ChatMessage'
import { TypingIndicator } from './TypingIndicator'
import { EmptyChat } from './EmptyChat'
import type { RAGMessage } from '../types'

interface ChatWindowProps {
  messages: RAGMessage[]
  loading?: boolean
  instanceName?: string
}

export function ChatWindow({ messages, loading, instanceName }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  if (messages.length === 0 && !loading) {
    return <EmptyChat instanceName={instanceName} />
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8">
      <div className="max-w-4xl mx-auto divide-y divide-border/30">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
