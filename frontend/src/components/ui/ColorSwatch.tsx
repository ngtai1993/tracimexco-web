import { cn } from '@/lib/utils'

interface ColorSwatchProps {
  value: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-5 h-5',
  md: 'w-7 h-7',
  lg: 'w-9 h-9',
}

export function ColorSwatch({ value, size = 'md', className }: ColorSwatchProps) {
  return (
    <span
      className={cn(
        'inline-block rounded border border-border/60 shrink-0',
        sizeClasses[size],
        className
      )}
      style={{ backgroundColor: value }}
      title={value}
    />
  )
}
