'use client'
import { Network, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useBuildGraph } from '../hooks'
import type { KnowledgeBase } from '../types'

interface GraphStatusCardProps {
  kb: KnowledgeBase
  onRefresh: () => void
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

const statusInfo: Record<string, { icon: React.ReactNode; text: string }> = {
  not_built: { icon: <Clock size={16} className="text-fg-subtle" />, text: 'Graph chưa được tạo' },
  building: { icon: <RefreshCw size={16} className="text-info animate-spin" />, text: 'Đang xây dựng graph...' },
  ready: { icon: <CheckCircle size={16} className="text-success" />, text: 'Graph đã sẵn sàng' },
  failed: { icon: <XCircle size={16} className="text-danger" />, text: 'Xây dựng graph thất bại' },
}

export function GraphStatusCard({ kb, onRefresh, onToast }: GraphStatusCardProps) {
  const { build, loading } = useBuildGraph()

  const status = kb.graph_status ?? 'not_built'
  const info = statusInfo[status] ?? statusInfo.not_built

  const handleBuild = async () => {
    const ok = await build(kb.slug)
    if (ok) {
      onToast('Đang xây dựng graph...', 'success')
      onRefresh()
    } else {
      onToast('Không thể bắt đầu xây dựng graph', 'danger')
    }
  }

  return (
    <div className="rounded-bento border border-border bg-card p-5">
      <div className="flex items-center gap-3 mb-4">
        <Network size={20} className="text-primary" />
        <h3 className="text-base font-semibold text-fg">Knowledge Graph</h3>
      </div>

      <div className="flex items-center gap-3 mb-4">
        {info.icon}
        <span className="text-sm text-fg">{info.text}</span>
        <StatusBadge status={status} className="ml-auto" />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div className="rounded-md bg-surface p-2">
          <p className="text-lg font-bold text-fg">{kb.document_count}</p>
          <p className="text-xs text-fg-muted">Documents</p>
        </div>
        <div className="rounded-md bg-surface p-2">
          <p className="text-lg font-bold text-fg">{kb.total_chunks}</p>
          <p className="text-xs text-fg-muted">Chunks</p>
        </div>
        <div className="rounded-md bg-surface p-2">
          <p className="text-lg font-bold text-fg">{kb.image_count}</p>
          <p className="text-xs text-fg-muted">Images</p>
        </div>
      </div>

      <Button
        size="sm"
        variant={status === 'building' ? 'ghost' : 'primary'}
        className="w-full"
        onClick={handleBuild}
        loading={loading}
        disabled={status === 'building'}
      >
        {status === 'building' ? 'Đang xây dựng...' : status === 'ready' ? 'Rebuild Graph' : 'Build Graph'}
      </Button>
    </div>
  )
}
