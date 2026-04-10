import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { fetchAppearanceConfig, buildCssVars } from '@/lib/appearance'
import { AppearanceProvider } from '@/features/appearance'
import './globals.css'

const inter = Inter({
  subsets: ['latin', 'vietnamese'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono-var',
  display: 'swap',
})

export const metadata: Metadata = {
  title: { default: 'App', template: '%s | App' },
  description: 'Powered by tracimexco-web',
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const config = await fetchAppearanceConfig()

  const lightCss =
    config?.colors?.light ? buildCssVars(config.colors.light, ':root') : ''
  const darkCss =
    config?.colors?.dark
      ? buildCssVars(config.colors.dark, '[data-theme="dark"]')
      : ''
  const themeCss = [lightCss, darkCss].filter(Boolean).join('\n\n')

  return (
    <html
      lang="vi"
      data-theme="light"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      {/* Next.js tự hoist <style> vào <head> — không cần tag <head> explicit */}
      {themeCss && (
        // eslint-disable-next-line react/no-danger
        <style dangerouslySetInnerHTML={{ __html: themeCss }} />
      )}
      <body className="min-h-dvh bg-bg text-fg font-sans antialiased">
        <AppearanceProvider config={config}>
          {children}
        </AppearanceProvider>
      </body>
    </html>
  );
}
