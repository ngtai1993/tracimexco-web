import { cn } from '@/lib/utils'
import type { BentoGridProps } from './types'

export function BentoGrid({ className, children }: BentoGridProps) {
  return (
    <div
      className={cn(
        'grid grid-cols-12 auto-rows-[minmax(120px,auto)] gap-4',
        className
      )}
    >
      {children}
    </div>
  )
}
