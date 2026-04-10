'use client'
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Toast, ToastVariant } from '@/hooks/useToast'

const variantConfig: Record<
  ToastVariant,
  { icon: React.ReactNode; classes: string }
> = {
  success: {
    icon: <CheckCircle2 size={18} />,
    classes: 'border-success/40 bg-success/10 text-success',
  },
  danger: {
    icon: <AlertCircle size={18} />,
    classes: 'border-danger/40 bg-danger/10 text-danger',
  },
  warning: {
    icon: <AlertTriangle size={18} />,
    classes: 'border-warning/40 bg-warning/10 text-warning',
  },
  info: {
    icon: <Info size={18} />,
    classes: 'border-info/40 bg-info/10 text-info',
  },
}

interface ToastItemProps {
  toast: Toast
  onRemove: (id: string) => void
}

export function ToastItem({ toast, onRemove }: ToastItemProps) {
  const config = variantConfig[toast.variant]
  return (
    <div
      className={cn(
        'flex items-start gap-3 px-4 py-3 rounded-bento border shadow-lg min-w-64 max-w-sm',
        'bg-surface text-fg',
        config.classes
      )}
      role="alert"
    >
      <span className="shrink-0 mt-0.5">{config.icon}</span>
      <p className="text-sm flex-1 text-fg">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="shrink-0 p-0.5 hover:opacity-70 transition-opacity"
        aria-label="Đóng thông báo"
      >
        <X size={14} />
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: Toast[]
  onRemove: (id: string) => void
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onRemove={onRemove} />
      ))}
    </div>
  )
}
