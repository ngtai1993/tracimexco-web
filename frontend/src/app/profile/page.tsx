import type { Metadata } from 'next'
import { ProfileCard } from '@/features/profile/components/ProfileCard'
import { ChangePasswordForm } from '@/features/profile/components/ChangePasswordForm'

export const metadata: Metadata = { title: 'Hồ sơ' }

export default function ProfilePage() {
  return (
    <div className="max-w-2xl flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-fg">Hồ sơ cá nhân</h1>
      <ProfileCard />
      <ChangePasswordForm />
    </div>
  )
}
