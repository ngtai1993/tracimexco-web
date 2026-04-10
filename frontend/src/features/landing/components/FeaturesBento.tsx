import { BentoGrid } from '@/components/bento/BentoGrid'
import { BentoCard } from '@/components/bento/BentoCard'
import { GradientText } from '@/components/gradient/GradientText'
import { Palette, Shield, Zap, Moon, Layout, RefreshCw } from 'lucide-react'

const features = [
  {
    icon: Palette,
    title: 'Dynamic Color System',
    desc: 'Toàn bộ màu sắc đến từ backend appearance API. Admin đổi màu — frontend cập nhật ngay.',
    size: '1x2' as const,
    gradient: 'primary' as const,
  },
  {
    icon: Moon,
    title: 'Dark Mode Mặc Định',
    desc: 'Dark mode là tiêu chuẩn. Bảo vệ mắt, tiết kiệm pin, trải nghiệm hiện đại.',
    size: '1x1' as const,
    gradient: 'accent' as const,
  },
  {
    icon: Layout,
    title: 'Bento Grid Layout',
    desc: 'Layout lưới bất đối xứng tạo chiều sâu thị giác.',
    size: '1x1' as const,
    gradient: 'surface' as const,
  },
  {
    icon: Zap,
    title: 'Next.js 15 + React 19',
    desc: 'Server Components, Server Actions, Streaming — kiến trúc tiên tiến nhất.',
    size: '2x1' as const,
    gradient: 'primary' as const,
  },
  {
    icon: Shield,
    title: 'Auth Bảo Mật',
    desc: 'httpOnly cookie, JWT refresh tự động, Zod validation.',
    size: '1x1' as const,
    gradient: 'surface' as const,
  },
  {
    icon: RefreshCw,
    title: 'On-demand Revalidation',
    desc: 'Cache thông minh — cập nhật ngay khi admin thay đổi.',
    size: '1x1' as const,
    gradient: 'accent' as const,
  },
]

export function FeaturesBento() {
  return (
    <section>
      <GradientText as="h2" className="text-3xl font-bold mb-2">
        Tính năng nổi bật
      </GradientText>
      <p className="text-fg-muted mb-8">
        Được tích hợp ngay từ đầu — không cần cài thêm plugin.
      </p>
      <BentoGrid>
        {features.map(({ icon: Icon, title, desc, size, gradient }) => (
          <BentoCard key={title} size={size} gradient={gradient}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-accent/20 flex items-center justify-center mb-4 shrink-0">
              <Icon size={20} className="text-primary" />
            </div>
            <h3 className="font-semibold text-fg mb-1">{title}</h3>
            <p className="text-sm text-fg-muted">{desc}</p>
          </BentoCard>
        ))}
      </BentoGrid>
    </section>
  )
}
