import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn('flex items-center gap-1.5 text-sm', className)}>
      <Link
        href="/dashboard"
        className="text-fg-muted hover:text-fg transition-colors"
      >
        <Home size={14} />
      </Link>
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1.5">
          <ChevronRight size={14} className="text-fg-subtle" />
          {item.href ? (
            <Link
              href={item.href}
              className="text-fg-muted hover:text-fg transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-fg font-medium">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
