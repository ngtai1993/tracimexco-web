import { cn } from '@/lib/utils'
import type { BentoCardProps, BentoSize, BentoVariant, BentoGradient } from './types'

const sizeClasses: Record<BentoSize, string> = {
  '1x1': 'col-span-12 row-span-2 sm:col-span-6 md:col-span-3',
  '2x1': 'col-span-12 row-span-2 sm:col-span-6 md:col-span-6',
  '1x2': 'col-span-12 row-span-4 sm:col-span-6 md:col-span-3',
  '2x2': 'col-span-12 row-span-4 sm:col-span-6 md:col-span-6',
  '3x1': 'col-span-12 row-span-2 md:col-span-9',
  'full': 'col-span-12 row-span-2',
}

const variantClasses: Record<BentoVariant, string> = {
  default: 'bg-surface border border-border',
  featured: 'gradient-border bg-surface',
  gradient: 'bg-gradient-to-br from-primary to-accent text-primary-fg border-0',
  ghost: 'bg-transparent border border-border/50',
}

const gradientClasses: Record<BentoGradient, string> = {
  primary: 'bg-gradient-to-br from-primary/20 to-accent/10',
  accent: 'bg-gradient-to-br from-accent/20 to-secondary/10',
  surface: 'bg-gradient-to-b from-surface to-bg',
  none: '',
}

export function BentoCard({
  size = '1x1',
  variant = 'default',
  gradient = 'none',
  hover = true,
  className,
  children,
}: BentoCardProps) {
  return (
    <div
      className={cn(
        'rounded-bento overflow-hidden p-5 flex flex-col',
        sizeClasses[size],
        variantClasses[variant],
        variant !== 'gradient' && gradientClasses[gradient],
        hover &&
          'transition-transform duration-200 hover:scale-[1.015] hover:shadow-lg',
        className
      )}
    >
      {children}
    </div>
  )
}
