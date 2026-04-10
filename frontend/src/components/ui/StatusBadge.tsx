import { cn } from '@/lib/utils'

type StatusColor = 'success' | 'warning' | 'danger' | 'info' | 'neutral'

interface StatusBadgeProps {
  status: string
  className?: string
}

const statusColorMap: Record<string, StatusColor> = {
  active: 'success',
  completed: 'success',
  ready: 'success',
  processing: 'info',
  building: 'info',
  pending: 'warning',
  not_built: 'neutral',
  inactive: 'neutral',
  failed: 'danger',
  error: 'danger',
  expired: 'danger',
}

const colorClasses: Record<StatusColor, string> = {
  success: 'bg-success/15 text-success',
  warning: 'bg-warning/15 text-warning',
  danger: 'bg-danger/15 text-danger',
  info: 'bg-info/15 text-info',
  neutral: 'bg-border/40 text-fg-muted',
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const color = statusColorMap[status] ?? 'neutral'

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium',
        colorClasses[color],
        className
      )}
    >
      <span
        className={cn(
          'w-1.5 h-1.5 rounded-full',
          color === 'success' && 'bg-success',
          color === 'warning' && 'bg-warning',
          color === 'danger' && 'bg-danger',
          color === 'info' && 'bg-info animate-pulse',
          color === 'neutral' && 'bg-fg-subtle'
        )}
      />
      {status.replace(/_/g, ' ')}
    </span>
  )
}
