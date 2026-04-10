import type { Metadata } from 'next'
import { fetchAppearanceConfig } from '@/lib/appearance'
import { Header } from '@/components/layout/Header'

export const metadata: Metadata = {
  title: { default: 'App', template: '%s | App' },
}

export default async function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const config = await fetchAppearanceConfig()

  return (
    <div className="min-h-dvh flex flex-col bg-bg">
      <Header appearance={config} user={null} />
      <div className="flex-1 flex min-h-0">
        {children}
      </div>
    </div>
  )
}
