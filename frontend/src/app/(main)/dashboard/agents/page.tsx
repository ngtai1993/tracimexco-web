'use client'
import { useState } from 'react'
import { Plus, Bot } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { ProviderCard, ProviderForm } from '@/features/agents'
import { useProviders } from '@/features/agents/hooks'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'

export default function AgentsOverviewPage() {
  const { providers, loading, error, refetch } = useProviders(true)
  const [showCreate, setShowCreate] = useState(false)
  const { toasts, addToast, removeToast } = useToast()

  const handleSuccess = () => {
    setShowCreate(false)
    addToast('Provider đã được tạo', 'success')
    refetch()
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">AI Providers</h1>
          <p className="text-sm text-fg-muted mt-1">Quản lý nhà cung cấp AI, API keys và cấu hình</p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus size={16} />
          Thêm Provider
        </Button>
      </div>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : providers.length === 0 ? (
        <EmptyState
          icon={<Bot size={40} strokeWidth={1.5} />}
          title="Chưa có provider nào"
          description="Thêm nhà cung cấp AI đầu tiên để bắt đầu"
          actionLabel="Thêm Provider"
          onAction={() => setShowCreate(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {providers.map((p) => (
            <ProviderCard key={p.id} provider={p} />
          ))}
        </div>
      )}

      <Modal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Tạo AI Provider mới"
        className="max-w-xl"
      >
        <ProviderForm onSuccess={handleSuccess} onCancel={() => setShowCreate(false)} />
      </Modal>
    </>
  )
}
