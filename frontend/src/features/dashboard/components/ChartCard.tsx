import { BentoCard } from '@/components/bento/BentoCard'
import { BarChart3 } from 'lucide-react'

export function ChartCard() {
  return (
    <BentoCard size="2x2" variant="featured">
      <p className="text-sm font-semibold text-fg mb-1">Thống kê</p>
      <p className="text-xs text-fg-muted mb-4">30 ngày gần nhất</p>
      {/* Chart placeholder */}
      <div className="flex-1 flex items-center justify-center rounded-bento border border-border/50 bg-bg/40">
        <div className="flex flex-col items-center gap-2 text-fg-subtle">
          <BarChart3 size={40} />
          <p className="text-sm">Chart sẽ được tích hợp</p>
        </div>
      </div>
    </BentoCard>
  )
}
