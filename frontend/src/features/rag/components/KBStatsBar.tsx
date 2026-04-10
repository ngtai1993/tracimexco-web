import { FileText, ImageIcon, Layers, Zap, CheckCircle2, AlertCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { KnowledgeBase } from '../types'

interface KBStatsBarProps {
  kb: KnowledgeBase
  className?: string
}

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  sub?: string
  iconBg: string
}

function StatCard({ icon, label, value, sub, iconBg }: StatCardProps) {
  return (
    <div className="bg-card border border-border rounded-bento p-4 flex items-start gap-3">
      <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0', iconBg)}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-fg-muted truncate">{label}</p>
        <p className="text-lg font-semibold text-fg leading-tight">{value}</p>
        {sub && <p className="text-xs text-fg-subtle mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

const graphStatusConfig = {
  ready: { icon: <CheckCircle2 size={16} className="text-success" />, label: 'Graph sẵn sàng', bg: 'bg-success/10' },
  building: { icon: <Clock size={16} className="text-info animate-spin" />, label: 'Đang xây dựng', bg: 'bg-info/10' },
  failed: { icon: <AlertCircle size={16} className="text-danger" />, label: 'Lỗi graph', bg: 'bg-danger/10' },
  not_built: { icon: <Layers size={16} className="text-fg-muted" />, label: 'Chưa xây dựng', bg: 'bg-surface' },
  null: { icon: <Layers size={16} className="text-fg-muted" />, label: 'Chưa xây dựng', bg: 'bg-surface' },
}

export function KBStatsBar({ kb, className }: KBStatsBarProps) {
  const gs = graphStatusConfig[(kb.graph_status ?? 'null') as keyof typeof graphStatusConfig]
    ?? graphStatusConfig.not_built

  return (
    <div className={cn('grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3', className)}>
      <StatCard
        icon={<FileText size={16} className="text-primary" />}
        iconBg="bg-primary/10"
        label="Tài liệu"
        value={kb.document_count}
        sub={kb.image_count > 0 ? `+ ${kb.image_count} ảnh` : undefined}
      />
      <StatCard
        icon={<ImageIcon size={16} className="text-info" />}
        iconBg="bg-info/10"
        label="Hình ảnh"
        value={kb.image_count}
        sub="image docs"
      />
      <StatCard
        icon={<Layers size={16} className="text-warning" />}
        iconBg="bg-warning/10"
        label="Tổng Chunks"
        value={kb.total_chunks.toLocaleString()}
        sub={`chunk size ${kb.chunk_size}`}
      />
      <StatCard
        icon={<Zap size={16} className="text-success" />}
        iconBg="bg-success/10"
        label="Model Embedding"
        value={kb.embedding_model.split('-').slice(-2).join('-')}
        sub={`${kb.embedding_dimensions}d`}
      />
      <StatCard
        icon={gs.icon}
        iconBg={gs.bg}
        label="Knowledge Graph"
        value={gs.label}
        sub={kb.chunk_strategy + ' chunk'}
      />
    </div>
  )
}
