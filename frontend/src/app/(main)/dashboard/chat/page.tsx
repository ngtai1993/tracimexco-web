'use client'
import { MessageSquare } from 'lucide-react'
import { InstanceSelector } from '@/features/chat'

export default function ChatPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg">Chat</h1>
        <p className="text-sm text-fg-muted mt-1">Chọn RAG instance để bắt đầu trò chuyện</p>
      </div>
      <InstanceSelector />
    </div>
  )
}
