'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSend: (query: string) => void
  loading?: boolean
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ onSend, loading, disabled, placeholder }: ChatInputProps) {
  const [query, setQuery] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = query.trim()
    if (!trimmed || loading || disabled) return
    onSend(trimmed)
    setQuery('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }, [query])

  return (
    <form onSubmit={handleSubmit} className="border-t border-border bg-card p-4">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? 'Nhập câu hỏi...'}
          rows={1}
          disabled={loading || disabled}
          className="flex-1 resize-none rounded-bento border border-border bg-surface px-4 py-3 text-sm text-fg placeholder:text-fg-subtle focus:border-primary focus:ring-1 focus:ring-primary/30 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!query.trim() || loading || disabled}
          className="shrink-0 rounded-bento bg-primary text-white p-3 hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </div>
    </form>
  )
}
