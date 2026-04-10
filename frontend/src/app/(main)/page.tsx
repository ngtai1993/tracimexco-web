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
    <main className="flex-1 mx-auto w-full max-w-7xl px-4 sm:px-6 py-8">
      <div className="flex flex-col gap-16">
        <HeroBento />
        <FeaturesBento />
        <CTASection />
      </div>
    </main>
  )
}
