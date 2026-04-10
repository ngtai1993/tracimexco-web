export type BentoSize = '1x1' | '2x1' | '1x2' | '2x2' | '3x1' | 'full'
export type BentoVariant = 'default' | 'featured' | 'gradient' | 'ghost'
export type BentoGradient = 'primary' | 'accent' | 'surface' | 'none'

export interface BentoCardProps {
  size?: BentoSize
  variant?: BentoVariant
  gradient?: BentoGradient
  hover?: boolean
  className?: string
  children: React.ReactNode
}

export interface BentoGridProps {
  className?: string
  children: React.ReactNode
}
