import { BentoGrid } from '@/components/bento/BentoGrid'
import { StatsCard } from './StatsCard'
import { ChartCard } from './ChartCard'
import { QuickActionsCard } from './QuickActionsCard'
import type { DashboardStat } from '../types'

const mockStats: DashboardStat[] = [
  { label: 'Tổng người dùng', value: '1,284', delta: '+12.5%', deltaPositive: true },
  { label: 'Đăng nhập hôm nay', value: '48', delta: '+3', deltaPositive: true },
  { label: 'Lỗi hệ thống', value: '2', delta: '-8', deltaPositive: true },
  { label: 'Uptime', value: '99.9%', delta: '30 ngày', deltaPositive: true },
]

export function DashboardBento() {
  return (
    <BentoGrid>
      {mockStats.map((stat) => (
        <StatsCard key={stat.label} stat={stat} />
      ))}
      <ChartCard />
      <QuickActionsCard />
    </BentoGrid>
  )
}
