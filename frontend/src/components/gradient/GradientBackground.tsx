import { cn } from '@/lib/utils'

type GradientDirection = 'to-br' | 'to-b' | 'to-r' | 'to-t'

interface GradientBackgroundProps {
  direction?: GradientDirection
  className?: string
  children: React.ReactNode
}

const directionMap: Record<GradientDirection, string> = {
  'to-br': 'bg-gradient-to-br from-primary/20 via-bg to-accent/10',
  'to-b':  'bg-gradient-to-b from-primary/30 to-bg',
  'to-r':  'bg-gradient-to-r from-primary/20 to-accent/15',
  'to-t':  'bg-gradient-to-t from-bg to-primary/20',
}

export function GradientBackground({
  direction = 'to-br',
  className,
  children,
}: GradientBackgroundProps) {
  return (
    <div className={cn('relative', directionMap[direction], className)}>
      {children}
    </div>
  )
}
