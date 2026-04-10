'use client'
import { User, Bot } from 'lucide-react'
import { cn } from '@/lib/utils'
import { MessageContent } from './MessageContent'
import { SourcesPanel } from './SourcesPanel'
import { ImageGallery } from './ImageGallery'
import { FeedbackButtons } from './FeedbackButtons'
import type { RAGMessage } from '../types'

interface ChatMessageProps {
  message: RAGMessage
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex gap-3 py-4', isUser && 'justify-end')}>
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot size={16} className="text-primary" />
        </div>
      )}

      <div className={cn('max-w-[75%] space-y-1', isUser && 'order-first')}>
        <div
          className={cn(
            'rounded-bento px-4 py-3',
            isUser
              ? 'bg-primary text-white rounded-br-sm'
              : 'bg-surface border border-border rounded-bl-sm'
          )}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <MessageContent content={message.content} />
          )}
        </div>

        {/* Assistant extras */}
        {!isUser && (
          <>
            <SourcesPanel sources={message.sources} />
            <ImageGallery images={message.images} />

            <div className="flex items-center gap-3">
              <FeedbackButtons
                messageId={message.id}
                currentFeedback={message.feedback}
              />
              {message.metadata && (
                <span className="text-[10px] text-fg-subtle">
                  {message.metadata.latency_ms}ms • {message.metadata.model}
                </span>
              )}
            </div>
          </>
        )}
      </div>

      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-fg/10 flex items-center justify-center">
          <User size={16} className="text-fg-muted" />
        </div>
      )}
    </div>
  )
}
