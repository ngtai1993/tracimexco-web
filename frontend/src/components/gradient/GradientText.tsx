import { cn } from '@/lib/utils'

type GradientFrom = 'primary' | 'accent' | 'secondary'
type GradientTo = 'primary' | 'accent' | 'secondary'

interface GradientTextProps {
  from?: GradientFrom
  to?: GradientTo
  className?: string
  as?: 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'p'
  children: React.ReactNode
}

export function GradientText({
  className,
  as: Tag = 'span',
  children,
}: GradientTextProps) {
  return (
    <Tag className={cn('gradient-text', className)}>
      {children}
    </Tag>
  )
}
