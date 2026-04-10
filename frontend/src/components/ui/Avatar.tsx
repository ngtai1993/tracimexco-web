import { cn } from '@/lib/utils'
import Image from 'next/image'
import { getInitials } from '@/lib/utils'

interface AvatarProps {
  src?: string | null
  name?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeMap = { sm: 32, md: 40, lg: 56 }
const textSizeMap = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' }

export function Avatar({ src, name, size = 'md', className }: AvatarProps) {
  const px = sizeMap[size]

  if (src) {
    return (
      <div
        className={cn('rounded-full overflow-hidden shrink-0 border border-border', className)}
        style={{ width: px, height: px }}
      >
        <Image src={src} alt={name ?? 'Avatar'} width={px} height={px} className="object-cover" />
      </div>
    )
  }

  return (
    <div
      className={cn(
        'rounded-full shrink-0 flex items-center justify-center font-semibold',
        'bg-gradient-to-br from-primary to-accent text-primary-fg',
        textSizeMap[size],
        className
      )}
      style={{ width: px, height: px }}
    >
      {name ? getInitials(name) : '?'}
    </div>
  )
}
