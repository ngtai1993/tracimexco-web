import type { Metadata } from 'next'
import { LoginForm } from '@/features/auth/components/LoginForm'
import { GradientText } from '@/components/gradient/GradientText'
import Link from 'next/link'

export const metadata: Metadata = { title: 'Đăng nhập' }

export default function LoginPage() {
  return (
    <div className="bg-surface border border-border rounded-bento p-8 shadow-2xl">
      <div className="text-center mb-8">
        <GradientText as="h1" className="text-3xl font-bold mb-2">
          Đăng nhập
        </GradientText>
        <p className="text-fg-muted text-sm">
          Chào mừng trở lại! Vui lòng đăng nhập để tiếp tục.
        </p>
      </div>
      <LoginForm />
      <p className="text-center text-sm text-fg-muted mt-6">
        Chưa có tài khoản?{' '}
        <Link href="/register" className="text-primary hover:underline font-medium">
          Đăng ký ngay
        </Link>
      </p>
    </div>
  )
}
