'use client'
import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { TokenTable } from '@/features/appearance/admin/components/TokenTable'
import { TokenForm } from '@/features/appearance/admin/components/TokenForm'
import type { ColorTokenAdmin } from '@/features/appearance/admin/types'

export default function TokensPage() {
  const [editTarget, setEditTarget] = useState<ColorTokenAdmin | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleSuccess = () => {
    setEditTarget(null)
    setShowCreate(false)
    setRefreshKey((k) => k + 1)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">Color Tokens</h1>
          <p className="text-sm text-fg-muted mt-1">Quản lý design token màu sắc light/dark</p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus size={16} />
          Thêm token
        </Button>
      </div>

      <TokenTable
        onEdit={(token) => setEditTarget(token)}
        refreshKey={refreshKey}
      />

      {/* Create modal */}
      <Modal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Tạo color token mới"
        className="max-w-xl"
      >
        <TokenForm
          onSuccess={handleSuccess}
          onCancel={() => setShowCreate(false)}
        />
      </Modal>

      {/* Edit modal */}
      <Modal
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        title={`Sửa token: ${editTarget?.key}`}
        className="max-w-xl"
      >
        <TokenForm
          token={editTarget}
          onSuccess={handleSuccess}
          onCancel={() => setEditTarget(null)}
        />
      </Modal>
    </div>
  )
}
