import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: { absolute: 'Đăng nhập | App' },
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-dvh bg-bg flex items-center justify-center relative overflow-hidden">
      {/* Background gradient blobs */}
      <div
        aria-hidden
        className="absolute inset-0 overflow-hidden pointer-events-none"
      >
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-primary/20 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-accent/15 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-4">
        {children}
      </div>
    </div>
  )
}
