import { cn } from '@/lib/utils'
import { InboxIcon } from 'lucide-react'
import { Button } from './Button'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  className?: string
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center gap-3 py-16 text-center', className)}>
      <div className="text-fg-subtle">
        {icon ?? <InboxIcon size={40} strokeWidth={1.5} />}
      </div>
      <h3 className="text-sm font-medium text-fg">{title}</h3>
      {description && <p className="text-sm text-fg-muted max-w-sm">{description}</p>}
      {actionLabel && onAction && (
        <Button size="sm" onClick={onAction} className="mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
