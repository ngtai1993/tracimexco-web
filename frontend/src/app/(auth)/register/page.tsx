import type { Metadata } from 'next'
import { RegisterForm } from '@/features/auth/components/RegisterForm'
import { GradientText } from '@/components/gradient/GradientText'
import Link from 'next/link'

export const metadata: Metadata = { title: 'Đăng ký' }

export default function RegisterPage() {
  return (
    <div className="bg-surface border border-border rounded-bento p-8 shadow-2xl">
      <div className="text-center mb-8">
        <GradientText as="h1" className="text-3xl font-bold mb-2">
          Tạo tài khoản
        </GradientText>
        <p className="text-fg-muted text-sm">
          Tham gia ngay để trải nghiệm đầy đủ tính năng.
        </p>
      </div>
      <RegisterForm />
      <p className="text-center text-sm text-fg-muted mt-6">
        Đã có tài khoản?{' '}
        <Link href="/login" className="text-primary hover:underline font-medium">
          Đăng nhập
        </Link>
      </p>
    </div>
  )
}
