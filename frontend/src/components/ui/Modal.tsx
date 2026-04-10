'use client'
import { useEffect, useRef } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  className?: string
}

export function Modal({ open, onClose, title, children, className }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === overlayRef.current && onClose()}
    >
      <div
        className={cn(
          'relative w-full max-w-md bg-surface border border-border rounded-bento p-6 shadow-2xl',
          'animate-in fade-in zoom-in-95 duration-200',
          className
        )}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-start justify-between mb-4">
          {title && <h2 className="text-lg font-semibold text-fg">{title}</h2>}
          <button
            onClick={onClose}
            className="ml-auto p-1 rounded-lg hover:bg-border/40 text-fg-muted hover:text-fg transition-colors"
            aria-label="Đóng"
          >
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
