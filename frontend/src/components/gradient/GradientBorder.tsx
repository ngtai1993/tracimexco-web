import { cn } from '@/lib/utils'

interface GradientBorderProps {
  className?: string
  children: React.ReactNode
  padding?: string
}

export function GradientBorder({
  className,
  children,
  padding = 'p-5',
}: GradientBorderProps) {
  return (
    <div className={cn('gradient-border', className)}>
      <div className={cn('rounded-bento bg-surface', padding)}>
        {children}
      </div>
    </div>
  )
}
