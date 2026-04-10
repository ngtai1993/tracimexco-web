import { Badge } from '@/components/ui/Badge'
import { STATUS_LABELS, STATUS_COLORS } from '../../constants'
import type { PostStatus } from '../../types'

interface PostStatusBadgeProps {
  status: PostStatus
  className?: string
}

const colorMap: Record<string, 'neutral' | 'warning' | 'info' | 'success' | 'danger'> = {
  neutral: 'neutral',
  warning: 'warning',
  info: 'info',
  success: 'success',
  danger: 'danger',
}

export function PostStatusBadge({ status, className }: PostStatusBadgeProps) {
  const color = colorMap[STATUS_COLORS[status]] ?? 'neutral'

  return (
    <Badge color={color} className={className}>
      {STATUS_LABELS[status]}
    </Badge>
  )
}
