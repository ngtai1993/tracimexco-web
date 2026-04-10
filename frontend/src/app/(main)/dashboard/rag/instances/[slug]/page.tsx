'use client'
import { useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Pencil, Trash2, Copy, Settings2, Database, Shield, BarChart3, Plus, X, ExternalLink, ArrowUpDown } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { Tabs } from '@/components/ui/Tabs'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonCard, SkeletonTable } from '@/components/ui/Skeleton'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import { InstanceForm, ConfigPanel, AnalyticsDashboard, UsageLogTable, AccessTable, AccessGrantForm } from '@/features/rag'
import { useInstance, useDeleteInstance, useCloneInstance, useInstanceKBs, useAssignKB, useKnowledgeBases } from '@/features/rag/hooks'
import { ragApi } from '@/features/rag/api'
import { Select } from '@/components/ui/Select'
import type { InstanceKBAssignment } from '@/features/rag/types'

// ── Inline KB management panel ────────────────────────────────────────────────
function InstanceKBsPanel({ instanceSlug, onToast }: { instanceSlug: string; onToast: (m: string, v: 'success' | 'danger') => void }) {
  const { assignments, loading, error, refetch } = useInstanceKBs(instanceSlug)
  const { assign, loading: assigning } = useAssignKB()
  const { kbs } = useKnowledgeBases()

  const [selectedKBId, setSelectedKBId] = useState('')
  const [priority, setPriority] = useState('1')
  const [removing, setRemoving] = useState<string | null>(null)

  const assignedIds = new Set(assignments.map((a) => a.knowledge_base.id))
  const availableKBs = kbs.filter((kb) => !assignedIds.has(kb.id))

  const handleAssign = useCallback(async () => {
    if (!selectedKBId) return
    const ok = await assign(instanceSlug, { knowledge_base_id: selectedKBId, priority: Number(priority) || 1 })
    if (ok) {
      onToast('Đã gán Knowledge Base', 'success')
      setSelectedKBId('')
      refetch()
    } else {
      onToast('Gán KB thất bại', 'danger')
    }
  }, [assign, instanceSlug, selectedKBId, priority, onToast, refetch])

  const handleRemove = useCallback(async (kbId: string) => {
    setRemoving(kbId)
    try {
      await ragApi.removeKBFromInstance(instanceSlug, kbId)
      onToast('Đã gỡ Knowledge Base', 'success')
      refetch()
    } catch {
      onToast('Gỡ KB thất bại', 'danger')
    } finally {
      setRemoving(null)
    }
  }, [instanceSlug, onToast, refetch])

  if (loading) return <SkeletonTable rows={3} />
  if (error) return <p className="text-sm text-danger py-4">{error}</p>

  return (
    <div className="space-y-4">
      {/* Assign form */}
      {availableKBs.length > 0 && (
        <div className="flex items-end gap-3 p-4 bg-surface border border-border rounded-bento">
          <div className="flex-1">
            <Select
              label="Thêm Knowledge Base"
              value={selectedKBId}
              onChange={(e) => setSelectedKBId(e.target.value)}
              placeholder="Chọn KB để gán..."
              options={availableKBs.map((kb) => ({ value: kb.id, label: kb.name }))}
            />
          </div>
          <div className="w-24">
            <Select
              label="Priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              options={[
                { value: '1', label: '1 (cao)' },
                { value: '2', label: '2' },
                { value: '3', label: '3' },
                { value: '4', label: '4' },
                { value: '5', label: '5 (thấp)' },
              ]}
            />
          </div>
          <Button
            size="sm"
            onClick={handleAssign}
            loading={assigning}
            disabled={!selectedKBId}
            className="mb-0.5"
          >
            <Plus size={14} /> Gán
          </Button>
        </div>
      )}

      {/* Assigned list */}
      {assignments.length === 0 ? (
        <div className="text-center py-12 text-fg-muted text-sm border border-dashed border-border rounded-bento">
          <Database size={32} strokeWidth={1.5} className="mx-auto mb-2 text-fg-subtle" />
          Chưa gán Knowledge Base nào. Thêm KB để instance có thể sử dụng dữ liệu.
        </div>
      ) : (
        <div className="space-y-2">
          {assignments
            .sort((a: InstanceKBAssignment, b: InstanceKBAssignment) => a.priority - b.priority)
            .map((assignment: InstanceKBAssignment) => {
              const kb = assignment.knowledge_base
              return (
                <div
                  key={kb.id}
                  className="flex items-center justify-between p-4 bg-card border border-border rounded-bento hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <ArrowUpDown size={13} className="text-primary" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-fg text-sm">{kb.name}</p>
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-border/50 text-fg-muted font-mono">
                          p={assignment.priority}
                        </span>
                      </div>
                      {kb.description && (
                        <p className="text-xs text-fg-muted truncate max-w-xs mt-0.5">{kb.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-1 text-[11px] text-fg-subtle">
                        <span>{kb.document_count} docs</span>
                        <span>·</span>
                        <span>{kb.total_chunks.toLocaleString()} chunks</span>
                        <span>·</span>
                        <StatusBadge status={kb.graph_status ?? 'not_built'} />
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Link
                      href={`/dashboard/rag/knowledge-bases/${kb.slug}`}
                      target="_blank"
                      className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors"
                      title="Mở Knowledge Base"
                    >
                      <ExternalLink size={14} />
                    </Link>
                    <button
                      onClick={() => handleRemove(kb.id)}
                      disabled={removing === kb.id}
                      className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors disabled:opacity-40"
                      title="Gỡ khỏi instance"
                    >
                      {removing === kb.id ? (
                        <span className="block w-3.5 h-3.5 border-2 border-danger/50 border-t-danger rounded-full animate-spin" />
                      ) : (
                        <X size={14} />
                      )}
                    </button>
                  </div>
                </div>
              )
            })}
        </div>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
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
        <InstanceKBsPanel instanceSlug={slug} onToast={addToast} />
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
