import Link from 'next/link'
import { BentoCard } from '@/components/bento/BentoCard'
import { GradientText } from '@/components/gradient/GradientText'
import { ArrowRight, UserCircle2, Settings } from 'lucide-react'

const actions = [
  { href: '/profile', label: 'Xem hồ sơ', icon: UserCircle2 },
  { href: '/settings', label: 'Cài đặt', icon: Settings },
]

export function QuickActionsCard() {
  return (
    <BentoCard size="full" variant="gradient">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <GradientText
            as="h3"
            className="text-lg font-bold text-primary-fg mb-1"
          >
            Thao tác nhanh
          </GradientText>
          <p className="text-primary-fg/70 text-sm">
            Điều hướng nhanh đến các chức năng chính
          </p>
        </div>
        <div className="flex gap-3 flex-wrap">
          {actions.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-2 px-4 py-2 rounded-bento bg-white/15 hover:bg-white/25 text-primary-fg text-sm font-medium transition-colors"
            >
              <Icon size={16} />
              {label}
              <ArrowRight size={14} />
            </Link>
          ))}
        </div>
      </div>
    </BentoCard>
  )
}
