import { cn } from '@/lib/utils'

type BadgeVariant = 'brand' | 'semantic' | 'outline' | 'gradient'
type BadgeColor = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'

interface BadgeProps {
  variant?: BadgeVariant
  color?: BadgeColor
  className?: string
  children: React.ReactNode
}

const colorClasses: Record<BadgeColor, string> = {
  primary: 'bg-primary/15 text-primary',
  success: 'bg-success/15 text-success',
  warning: 'bg-warning/15 text-warning',
  danger: 'bg-danger/15 text-danger',
  info: 'bg-info/15 text-info',
  neutral: 'bg-border/40 text-fg-muted',
}

export function Badge({
  variant = 'brand',
  color = 'primary',
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium',
        variant === 'gradient'
          ? 'bg-gradient-to-r from-primary to-accent text-primary-fg'
          : variant === 'outline'
          ? 'border border-current bg-transparent ' + colorClasses[color]
          : colorClasses[color],
        className
      )}
    >
      {children}
    </span>
  )
}
