import Link from 'next/link'
import { AppLogo } from './AppLogo'
import { ThemeToggle } from './ThemeToggle'
import { Avatar } from '@/components/ui/Avatar'
import type { AppearanceConfig } from '@/types/appearance'

interface HeaderProps {
  appearance?: AppearanceConfig | null
  user?: { full_name: string; email: string } | null
}

const navLinks = [
  { href: '/', label: 'Trang chủ' },
  { href: '/dashboard', label: 'Dashboard' },
]

export function Header({ appearance, user }: HeaderProps) {
  const logoSrc = appearance?.media?.logo ?? null

  return (
    <header className="sticky top-0 z-40 h-16 border-b border-border bg-bg/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl h-full px-4 sm:px-6 flex items-center justify-between gap-4">
        <AppLogo src={logoSrc} />

        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="px-3 py-1.5 rounded-lg text-sm text-fg-muted hover:text-fg hover:bg-surface transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          {user ? (
            <Link href="/profile">
              <Avatar name={user.full_name} size="sm" />
            </Link>
          ) : (
            <Link
              href="/login"
              className="px-4 py-1.5 rounded-bento text-sm font-medium bg-primary text-primary-fg hover:bg-primary-hover transition-colors"
            >
              Đăng nhập
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
