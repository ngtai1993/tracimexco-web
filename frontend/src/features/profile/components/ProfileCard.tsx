import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { formatDate } from '@/lib/utils'

// Placeholder — will be replaced with real data from cookie/server
const mockUser = {
  full_name: 'Người dùng',
  email: 'user@example.com',
  date_joined: new Date().toISOString(),
}

export function ProfileCard() {
  return (
    <div className="bg-surface border border-border rounded-bento p-6 flex items-start gap-5">
      <Avatar name={mockUser.full_name} size="lg" />
      <div className="flex-1">
        <div className="flex items-center gap-3 flex-wrap mb-1">
          <h2 className="text-lg font-semibold text-fg">{mockUser.full_name}</h2>
          <Badge color="primary">Người dùng</Badge>
        </div>
        <p className="text-sm text-fg-muted mb-3">{mockUser.email}</p>
        <p className="text-xs text-fg-subtle">
          Tham gia: {formatDate(mockUser.date_joined)}
        </p>
      </div>
    </div>
  )
}
