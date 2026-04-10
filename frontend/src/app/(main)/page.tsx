import type { Metadata } from 'next'
import { HeroBento } from '@/features/landing/components/HeroBento'
import { FeaturesBento } from '@/features/landing/components/FeaturesBento'
import { CTASection } from '@/features/landing/components/CTASection'

export const metadata: Metadata = {
  title: 'Trang chủ',
  description: 'Nền tảng quản lý hiện đại với Dark Azure design system',
}

export default function LandingPage() {
  return (
    <div className="flex flex-col gap-16">
      <HeroBento />
      <FeaturesBento />
      <CTASection />
    </div>
  )
}
