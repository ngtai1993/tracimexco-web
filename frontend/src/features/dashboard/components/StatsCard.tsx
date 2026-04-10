import { BentoCard } from '@/components/bento/BentoCard'
import type { DashboardStat } from '../types'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  stat: DashboardStat
}

export function StatsCard({ stat }: StatsCardProps) {
  return (
    <BentoCard size="1x1" variant="default" gradient="surface">
      <p className="text-xs font-medium text-fg-muted uppercase tracking-wider mb-3">
        {stat.label}
      </p>
      <p className="text-3xl font-bold text-fg flex-1">{stat.value}</p>
      {stat.delta && (
        <div
          className={`flex items-center gap-1 text-xs font-medium mt-2 ${
            stat.deltaPositive ? 'text-success' : 'text-danger'
          }`}
        >
          {stat.deltaPositive ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {stat.delta}
        </div>
      )}
    </BentoCard>
  )
}
