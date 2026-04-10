'use client'
import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Pencil, Trash2, Copy, Settings2, Database, Shield, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Tabs } from '@/components/ui/Tabs'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import { InstanceForm, ConfigPanel, AnalyticsDashboard, UsageLogTable, AccessTable, AccessGrantForm } from '@/features/rag'
import { useInstance, useDeleteInstance, useCloneInstance } from '@/features/rag/hooks'

export default function InstanceDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const router = useRouter()
  const { instance, loading, refetch } = useInstance(slug)
  const { remove, loading: deleting } = useDeleteInstance()
  const { clone, loading: cloning } = useCloneInstance()

  const [activeTab, setActiveTab] = useState('config')
  const [showEdit, setShowEdit] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [showClone, setShowClone] = useState(false)
  const [cloneName, setCloneName] = useState('')
  const [cloneSlug, setCloneSlug] = useState('')
  const [showGrantAccess, setShowGrantAccess] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const { toasts, addToast, removeToast } = useToast()

  const handleDelete = async () => {
    const ok = await remove(slug)
    if (ok) router.push('/dashboard/rag')
  }

  const handleClone = async () => {
    if (!cloneName || !cloneSlug) return
    const result = await clone(slug, { new_name: cloneName, new_slug: cloneSlug })
    if (result) {
      addToast('Đã clone instance', 'success')
      setShowClone(false)
      router.push(`/dashboard/rag/instances/${result.slug}`)
    }
  }

  if (loading) return <SkeletonCard />
  if (!instance) {
    return (
      <div className="text-center py-16">
        <p className="text-lg text-fg-muted">Instance không tồn tại</p>
        <Link href="/dashboard/rag" className="text-primary hover:underline text-sm mt-2 block">
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
          { label: 'RAG System', href: '/dashboard/rag' },
          { label: instance.name },
        ]}
        className="mb-4"
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">{instance.name}</h1>
          <p className="text-sm text-fg-muted mt-1">{instance.description || instance.purpose}</p>
          <div className="flex items-center gap-2 mt-2">
            <StatusBadge status={instance.is_active ? 'active' : 'inactive'} />
            <span className="text-xs text-fg-muted">{instance.provider_name}</span>
            {instance.is_public && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-info/15 text-info font-medium">Public</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setShowClone(true)}>
            <Copy size={14} /> Clone
          </Button>
          <Button size="sm" variant="outline" onClick={() => setShowEdit(true)}>
            <Pencil size={14} /> Sửa
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setShowDelete(true)} className="text-danger hover:bg-danger/10">
            <Trash2 size={14} />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { key: 'config', label: 'Cấu hình', icon: <Settings2 size={14} /> },
          { key: 'kbs', label: 'Knowledge Bases', icon: <Database size={14} /> },
          { key: 'access', label: 'Quyền truy cập', icon: <Shield size={14} /> },
          { key: 'analytics', label: 'Analytics', icon: <BarChart3 size={14} /> },
        ]}
        active={activeTab}
        onChange={setActiveTab}
        className="mb-6"
      />

      {activeTab === 'config' && (
        <ConfigPanel
          instance={instance}
          onUpdated={refetch}
          onToast={addToast}
        />
      )}

      {activeTab === 'kbs' && (
        <div>
          <div className="mb-4">
            <Link href={`/dashboard/rag/instances/${slug}/knowledge-bases`}>
              <Button size="sm" variant="outline">
                <Database size={14} /> Quản lý KB gán cho instance
              </Button>
            </Link>
          </div>
          <p className="text-sm text-fg-muted">
            Truy cập trang quản lý KB để gán/bỏ gán knowledge base cho instance này.
          </p>
        </div>
      )}

      {activeTab === 'access' && (
        <div>
          <div className="flex justify-end mb-4">
            <Button size="sm" onClick={() => setShowGrantAccess(true)}>
              <Shield size={14} /> Cấp quyền
            </Button>
          </div>
          <AccessTable
            instanceSlug={slug}
            onAdd={() => setShowGrantAccess(true)}
            refreshKey={refreshKey}
            onToast={addToast}
          />
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-8">
          <AnalyticsDashboard instanceSlug={slug} />
          <div>
            <h3 className="text-sm font-semibold text-fg mb-3">Usage Logs</h3>
            <UsageLogTable instanceSlug={slug} />
          </div>
        </div>
      )}

      {/* Edit Modal */}
      <Modal open={showEdit} onClose={() => setShowEdit(false)} title="Sửa Instance" className="max-w-xl">
        <InstanceForm
          instance={instance}
          onSuccess={() => { setShowEdit(false); refetch(); addToast('Đã cập nhật', 'success') }}
          onCancel={() => setShowEdit(false)}
        />
      </Modal>

      {/* Delete Confirm */}
      <ConfirmDialog
        open={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa Instance"
        message={`Bạn chắc chắn muốn xóa "${instance.name}"?`}
        confirmLabel="Xóa"
      />

      {/* Clone Modal */}
      <Modal open={showClone} onClose={() => setShowClone(false)} title="Clone Instance" className="max-w-md">
        <div className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-fg mb-1">Tên mới</label>
            <input
              className="w-full rounded-bento border border-border bg-surface px-3 py-2 text-sm text-fg focus:border-primary focus:ring-1 focus:ring-primary/30"
              value={cloneName}
              onChange={(e) => setCloneName(e.target.value)}
              placeholder={`${instance.name} (Copy)`}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-fg mb-1">Slug mới</label>
            <input
              className="w-full rounded-bento border border-border bg-surface px-3 py-2 text-sm text-fg focus:border-primary focus:ring-1 focus:ring-primary/30"
              value={cloneSlug}
              onChange={(e) => setCloneSlug(e.target.value)}
              placeholder={`${slug}-copy`}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={() => setShowClone(false)}>Hủy</Button>
            <Button size="sm" loading={cloning} onClick={handleClone}>Clone</Button>
          </div>
        </div>
      </Modal>

      {/* Grant Access Modal */}
      <Modal open={showGrantAccess} onClose={() => setShowGrantAccess(false)} title="Cấp quyền truy cập" className="max-w-md">
        <AccessGrantForm
          instanceSlug={slug}
          onSuccess={() => {
            setShowGrantAccess(false)
            setRefreshKey(k => k + 1)
            addToast('Đã cấp quyền', 'success')
          }}
          onCancel={() => setShowGrantAccess(false)}
        />
      </Modal>
    </>
  )
}
