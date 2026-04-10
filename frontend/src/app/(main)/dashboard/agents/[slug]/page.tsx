'use client'
import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Plus, Pencil, Trash2, Key, Sliders } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Tabs } from '@/components/ui/Tabs'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import { KeyTable, KeyForm, ConfigTable, ConfigForm, ProviderForm } from '@/features/agents'
import { useProviders, useDeleteProvider } from '@/features/agents/hooks'
import type { AgentAPIKey, AgentConfig } from '@/features/agents/types'

export default function ProviderDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const router = useRouter()
  const { providers, loading, refetch } = useProviders(true)
  const provider = providers.find(p => p.slug === slug) ?? null
  const { remove, loading: deleting } = useDeleteProvider()

  const [activeTab, setActiveTab] = useState('keys')
  const [showEdit, setShowEdit] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [showAddKey, setShowAddKey] = useState(false)
  const [editKey, setEditKey] = useState<AgentAPIKey | null>(null)
  const [showAddConfig, setShowAddConfig] = useState(false)
  const [editConfig, setEditConfig] = useState<AgentConfig | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const { toasts, addToast, removeToast } = useToast()

  const handleDelete = async () => {
    if (!provider) return
    const ok = await remove(provider.slug)
    if (ok) {
      router.push('/dashboard/agents')
    }
  }

  if (loading) return <SkeletonCard />
  if (!provider) {
    return (
      <div className="text-center py-16">
        <p className="text-lg text-fg-muted">Provider không tồn tại</p>
        <Link href="/dashboard/agents" className="text-primary hover:underline text-sm mt-2 block">
          ← Quay lại
        </Link>
      </div>
    )
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <Breadcrumb
        items={[
          { label: 'AI Providers', href: '/dashboard/agents' },
          { label: provider.name },
        ]}
        className="mb-4"
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">{provider.name}</h1>
          <p className="text-sm text-fg-muted mt-1">{provider.description || `slug: ${provider.slug}`}</p>
          <div className="flex items-center gap-2 mt-2">
            <StatusBadge status={provider.is_active ? 'active' : 'inactive'} />
            <span className="text-xs text-fg-muted">
              {provider.active_keys_count}/{provider.keys_count} keys active
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setShowEdit(true)}>
            <Pencil size={14} /> Sửa
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setShowDelete(true)} className="text-danger hover:bg-danger/10">
            <Trash2 size={14} /> Xóa
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { key: 'keys', label: 'API Keys', icon: <Key size={14} /> },
          { key: 'configs', label: 'Configs', icon: <Sliders size={14} /> },
        ]}
        active={activeTab}
        onChange={setActiveTab}
        className="mb-6"
      />

      {activeTab === 'keys' && (
        <div>
          <div className="flex justify-end mb-4">
            <Button size="sm" onClick={() => setShowAddKey(true)}>
              <Plus size={14} /> Thêm API Key
            </Button>
          </div>
          <KeyTable
            providerSlug={slug}
            onEdit={setEditKey}
            onAdd={() => setShowAddKey(true)}
            refreshKey={refreshKey}
            onToast={addToast}
          />
        </div>
      )}

      {activeTab === 'configs' && (
        <div>
          <div className="flex justify-end mb-4">
            <Button size="sm" onClick={() => setShowAddConfig(true)}>
              <Plus size={14} /> Thêm Config
            </Button>
          </div>
          <ConfigTable
            providerSlug={slug}
            onEdit={setEditConfig}
            onAdd={() => setShowAddConfig(true)}
            refreshKey={refreshKey}
            onToast={addToast}
          />
        </div>
      )}

      {/* Edit Provider Modal */}
      <Modal open={showEdit} onClose={() => setShowEdit(false)} title="Sửa Provider" className="max-w-xl">
        <ProviderForm
          provider={provider}
          onSuccess={() => { setShowEdit(false); refetch(); addToast('Đã cập nhật provider', 'success') }}
          onCancel={() => setShowEdit(false)}
        />
      </Modal>

      {/* Delete Confirm */}
      <ConfirmDialog
        open={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa Provider"
        message={`Bạn chắc chắn muốn xóa "${provider.name}"? Tất cả keys và configs sẽ bị xóa.`}
        confirmLabel="Xóa"
      />

      {/* Add/Edit Key Modal */}
      <Modal
        open={showAddKey || !!editKey}
        onClose={() => { setShowAddKey(false); setEditKey(null) }}
        title={editKey ? `Sửa key: ${editKey.name}` : 'Thêm API Key'}
        className="max-w-lg"
      >
        <KeyForm
          providerSlug={slug}
          apiKey={editKey}
          onSuccess={() => {
            setShowAddKey(false)
            setEditKey(null)
            setRefreshKey(k => k + 1)
            addToast(editKey ? 'Đã cập nhật key' : 'Đã thêm key', 'success')
          }}
          onCancel={() => { setShowAddKey(false); setEditKey(null) }}
        />
      </Modal>

      {/* Add/Edit Config Modal */}
      <Modal
        open={showAddConfig || !!editConfig}
        onClose={() => { setShowAddConfig(false); setEditConfig(null) }}
        title={editConfig ? `Sửa config: ${editConfig.name}` : 'Thêm Config'}
        className="max-w-lg"
      >
        <ConfigForm
          providerSlug={slug}
          config={editConfig}
          onSuccess={() => {
            setShowAddConfig(false)
            setEditConfig(null)
            setRefreshKey(k => k + 1)
            addToast(editConfig ? 'Đã cập nhật config' : 'Đã thêm config', 'success')
          }}
          onCancel={() => { setShowAddConfig(false); setEditConfig(null) }}
        />
      </Modal>
    </>
  )
}
