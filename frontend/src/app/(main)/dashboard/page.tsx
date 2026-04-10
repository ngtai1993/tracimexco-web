import type { Metadata } from 'next'
import { DashboardBento } from '@/features/dashboard/components/DashboardBento'

export const metadata: Metadata = { title: 'Dashboard' }

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-fg mb-6">Dashboard</h1>
      <DashboardBento />
    </div>
  )
}
