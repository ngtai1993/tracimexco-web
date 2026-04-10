'use client'
import { useParams } from 'next/navigation'
import { ChatLayout } from '@/features/chat'
import { useInstance } from '@/features/rag/hooks'

export default function ChatConversationPage() {
  const { slug, conversationId } = useParams<{ slug: string; conversationId: string }>()
  const { instance } = useInstance(slug)

  return (
    <ChatLayout
      instanceSlug={slug}
      instanceName={instance?.name}
      conversationId={conversationId}
    />
  )
}
