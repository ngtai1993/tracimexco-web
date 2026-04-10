'use client'
import { useParams } from 'next/navigation'
import { ChatLayout } from '@/features/chat'
import { useInstance } from '@/features/rag/hooks'

export default function ChatInstancePage() {
  const { slug } = useParams<{ slug: string }>()
  const { instance } = useInstance(slug)

  return (
    <ChatLayout
      instanceSlug={slug}
      instanceName={instance?.name}
    />
  )
}
