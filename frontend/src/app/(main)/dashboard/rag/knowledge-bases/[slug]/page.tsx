'use client'
import { useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import { DocumentTable, DocumentUploadForm, ChunkViewer, GraphStatusCard } from '@/features/rag'
import { useKnowledgeBase } from '@/features/rag/hooks'
import type { Document } from '@/features/rag/types'

export default function KBDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const { kb, loading, refetch } = useKnowledgeBase(slug)

  const [showUpload, setShowUpload] = useState(false)
  const [viewChunksDoc, setViewChunksDoc] = useState<Document | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const { toasts, addToast, removeToast } = useToast()

  if (loading) return <SkeletonCard />
  if (!kb) {
    return (
      <div className="text-center py-16">
        <p className="text-lg text-fg-muted">Knowledge Base không tồn tại</p>
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
          { label: kb.name },
        ]}
        className="mb-4"
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">{kb.name}</h1>
          <p className="text-sm text-fg-muted mt-1">
            {kb.description || `${kb.document_count} documents • ${kb.total_chunks} chunks`}
          </p>
          <div className="flex items-center gap-3 mt-2 text-xs text-fg-muted">
            <span className="capitalize">{kb.chunk_strategy}</span>
            <span>•</span>
            <span>Chunk: {kb.chunk_size}/{kb.chunk_overlap}</span>
            <span>•</span>
            <span>{kb.embedding_model}</span>
            <span>•</span>
            <span>{kb.embedding_dimensions}d</span>
          </div>
        </div>
        <Button size="sm" onClick={() => setShowUpload(true)}>
          <Plus size={14} /> Thêm tài liệu
        </Button>
      </div>

      {/* Graph Status + Documents side by side on large screens */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        <div className="lg:col-span-1">
          <GraphStatusCard kb={kb} onRefresh={refetch} onToast={addToast} />
        </div>
        <div className="lg:col-span-3">
          {viewChunksDoc ? (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-fg">Chunks</h3>
                <Button size="sm" variant="ghost" onClick={() => setViewChunksDoc(null)}>
                  ← Back to documents
                </Button>
              </div>
              <ChunkViewer docId={viewChunksDoc.id} docTitle={viewChunksDoc.title} />
            </div>
          ) : (
            <DocumentTable
              kbSlug={slug}
              onViewChunks={setViewChunksDoc}
              onAdd={() => setShowUpload(true)}
              refreshKey={refreshKey}
              onToast={addToast}
            />
          )}
        </div>
      </div>

      {/* Upload Modal */}
      <Modal open={showUpload} onClose={() => setShowUpload(false)} title="Thêm tài liệu" className="max-w-lg">
        <DocumentUploadForm
          kbSlug={slug}
          onSuccess={() => {
            setShowUpload(false)
            setRefreshKey(k => k + 1)
            addToast('Đã thêm tài liệu', 'success')
          }}
          onCancel={() => setShowUpload(false)}
        />
      </Modal>
    </>
  )
}
