import Link from 'next/link'
import { GradientBackground } from '@/components/gradient/GradientBackground'
import { GradientText } from '@/components/gradient/GradientText'
import { ArrowRight } from 'lucide-react'

export function CTASection() {
  return (
    <GradientBackground
      direction="to-r"
      className="rounded-bento border border-primary/20 px-8 py-16 text-center"
    >
      <GradientText as="h2" className="text-4xl font-bold mb-4">
        Bắt đầu ngay hôm nay
      </GradientText>
      <p className="text-fg-muted max-w-lg mx-auto mb-8">
        Đăng ký miễn phí và trải nghiệm nền tảng quản lý được xây dựng
        với các công nghệ tiên tiến nhất.
      </p>
      <Link
        href="/register"
        className="inline-flex items-center gap-2 px-8 py-3 rounded-bento bg-gradient-to-r from-primary to-accent text-primary-fg font-semibold hover:brightness-110 transition-all active:scale-95"
      >
        Tạo tài khoản miễn phí <ArrowRight size={18} />
      </Link>
    </GradientBackground>
  )
}
