import Link from 'next/link'
import {
  LayoutDashboard,
  User,
  LogOut,
  Settings,
  Palette,
  Bot,
  Brain,
  MessageSquare,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/agents', label: 'AI Providers', icon: Bot },
  { href: '/dashboard/rag', label: 'RAG System', icon: Brain },
  { href: '/dashboard/chat', label: 'Chat', icon: MessageSquare },
  { href: '/dashboard/appearance', label: 'Appearance', icon: Palette },
  { href: '/profile', label: 'Hồ sơ', icon: User },
  { href: '/settings', label: 'Cài đặt', icon: Settings },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  return (
    <aside
      className={cn(
        'w-56 shrink-0 border-r border-border bg-bg flex flex-col py-4',
        className
      )}
    >
      <nav className="flex-1 px-2 flex flex-col gap-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-3 px-3 py-2 rounded-bento text-sm text-fg-muted hover:text-fg hover:bg-surface transition-colors"
          >
            <Icon size={17} />
            {label}
          </Link>
        ))}
      </nav>

      <div className="px-2">
        <form action="/api/auth/logout" method="post">
          <button
            type="submit"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-bento text-sm text-fg-muted hover:text-danger hover:bg-danger/10 transition-colors"
          >
            <LogOut size={17} />
            Đăng xuất
          </button>
        </form>
      </div>
    </aside>
  )
}
