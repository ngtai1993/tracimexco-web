'use client'
import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { AssetGrid } from '@/features/appearance/admin/components/AssetGrid'
import { AssetForm } from '@/features/appearance/admin/components/AssetForm'
import type { MediaAssetAdmin } from '@/features/appearance/admin/types'

export default function AssetsPage() {
  const [editTarget, setEditTarget] = useState<MediaAssetAdmin | null>(null)
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
          <h1 className="text-2xl font-semibold text-fg">Media Assets</h1>
          <p className="text-sm text-fg-muted mt-1">Logo, favicon, banner và các ảnh hệ thống</p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus size={16} />
          Upload asset
        </Button>
      </div>

      <AssetGrid
        onEdit={(asset) => setEditTarget(asset)}
        refreshKey={refreshKey}
      />

      {/* Create modal */}
      <Modal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Upload media asset mới"
        className="max-w-lg"
      >
        <AssetForm
          onSuccess={handleSuccess}
          onCancel={() => setShowCreate(false)}
        />
      </Modal>

      {/* Edit modal */}
      <Modal
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        title={`Sửa asset: ${editTarget?.key}`}
        className="max-w-lg"
      >
        <AssetForm
          asset={editTarget}
          onSuccess={handleSuccess}
          onCancel={() => setEditTarget(null)}
        />
      </Modal>
    </div>
  )
}
