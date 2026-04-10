import { BentoGrid } from '@/components/bento/BentoGrid'
import { BentoCard } from '@/components/bento/BentoCard'
import { GradientText } from '@/components/gradient/GradientText'
import Link from 'next/link'
import { ArrowRight, Zap } from 'lucide-react'

export function HeroBento() {
  return (
    <BentoGrid>
      {/* Hero — full width */}
      <BentoCard size="full" variant="gradient" hover={false} className="min-h-[280px]">
        <div className="flex flex-col justify-between h-full">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 text-primary-fg/80 text-xs font-medium w-fit">
            <Zap size={12} />
            Dark Azure Design System
          </span>
          <div>
            <h1 className="text-4xl sm:text-5xl font-bold text-primary-fg mb-3 leading-tight">
              Nền tảng quản lý<br />
              <span className="text-white/80">hiện đại &amp; mạnh mẽ</span>
            </h1>
            <p className="text-primary-fg/70 text-base mb-6 max-w-xl">
              Được xây dựng với Next.js 15, Bento Grid Layout và hệ thống màu sắc
              động từ backend — không hardcode một màu hex nào.
            </p>
            <div className="flex gap-3 flex-wrap">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-bento bg-white text-primary font-semibold hover:bg-white/90 transition-colors"
              >
                Bắt đầu ngay <ArrowRight size={16} />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-bento bg-white/15 text-primary-fg font-medium hover:bg-white/25 transition-colors"
              >
                Đăng nhập
              </Link>
            </div>
          </div>
        </div>
      </BentoCard>
    </BentoGrid>
  )
}
