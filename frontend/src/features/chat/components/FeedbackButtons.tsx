'use client'
import { useState } from 'react'
import { ThumbsUp, ThumbsDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSubmitFeedback } from '../hooks'

interface FeedbackButtonsProps {
  messageId: string
  currentFeedback: 'positive' | 'negative' | null
  onFeedbackSent?: () => void
}

export function FeedbackButtons({ messageId, currentFeedback, onFeedbackSent }: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState(currentFeedback)
  const [showComment, setShowComment] = useState(false)
  const [comment, setComment] = useState('')
  const { submit, loading } = useSubmitFeedback()

  const handleFeedback = async (type: 'positive' | 'negative') => {
    if (loading) return
    const ok = await submit(messageId, { feedback: type, comment: comment || undefined })
    if (ok) {
      setFeedback(type)
      setShowComment(false)
      onFeedbackSent?.()
    }
  }

  return (
    <div className="flex items-center gap-1 mt-1">
      <button
        onClick={() => handleFeedback('positive')}
        disabled={loading}
        className={cn(
          'p-1 rounded hover:bg-success/10 transition-colors',
          feedback === 'positive' ? 'text-success' : 'text-fg-subtle hover:text-success'
        )}
        title="Hữu ích"
      >
        <ThumbsUp size={13} />
      </button>
      <button
        onClick={() => {
          if (feedback === 'negative') return
          setShowComment(true)
        }}
        disabled={loading}
        className={cn(
          'p-1 rounded hover:bg-danger/10 transition-colors',
          feedback === 'negative' ? 'text-danger' : 'text-fg-subtle hover:text-danger'
        )}
        title="Không hữu ích"
      >
        <ThumbsDown size={13} />
      </button>

      {showComment && (
        <div className="flex items-center gap-1.5 ml-2">
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Nhận xét..."
            className="text-xs border border-border rounded px-2 py-1 bg-surface text-fg w-40 focus:border-primary focus:ring-1 focus:ring-primary/30"
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleFeedback('negative')
              if (e.key === 'Escape') setShowComment(false)
            }}
          />
          <button
            onClick={() => handleFeedback('negative')}
            className="text-xs text-danger hover:text-danger/80"
          >
            Gửi
          </button>
        </div>
      )}
    </div>
  )
}
