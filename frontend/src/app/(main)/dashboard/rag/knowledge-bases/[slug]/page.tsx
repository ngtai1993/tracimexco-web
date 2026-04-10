'use client'
import { useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Plus, Settings2, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Breadcrumb } from '@/components/ui/Breadcrumb'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import {
  KBStatsBar,
  DocumentTable,
  DocumentPreviewPanel,
  DocumentUploadForm,
  ChunkViewer,
  GraphStatusCard,
} from '@/features/rag'
import { useKnowledgeBase } from '@/features/rag/hooks'
import type { Document } from '@/features/rag/types'

export default function KBDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const { kb, loading, refetch } = useKnowledgeBase(slug)

  const [showUpload, setShowUpload] = useState(false)
  const [showGraphPanel, setShowGraphPanel] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [viewChunksDoc, setViewChunksDoc] = useState<Document | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const { toasts, addToast, removeToast } = useToast()

  const handleSelectDoc = (doc: Document) => {
    // Toggle: click same doc → close panel
    setSelectedDoc((prev) => (prev?.id === doc.id ? null : doc))
    setViewChunksDoc(null)
  }

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

      {/* Overlay dim khi panel mở */}
      {selectedDoc && (
        <div
          className="fixed inset-0 z-30 bg-black/20"
          onClick={() => setSelectedDoc(null)}
        />
      )}

      <Breadcrumb
        items={[
          { label: 'RAG System', href: '/dashboard/rag' },
          { label: kb.name },
        ]}
        className="mb-4"
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <h1 className="text-2xl font-semibold text-fg">{kb.name}</h1>
          {kb.description && (
            <p className="text-sm text-fg-muted mt-1 max-w-xl">{kb.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowGraphPanel((v) => !v)}
            title="Knowledge Graph"
          >
            <Settings2 size={14} />
          </Button>
          <Button size="sm" onClick={() => setShowUpload(true)}>
            <Plus size={14} /> Thêm tài liệu
          </Button>
        </div>
      </div>

      {/* Stats bar */}
      <KBStatsBar kb={kb} className="mb-6" />

      {/* Graph panel (collapsible) */}
      {showGraphPanel && (
        <div className="mb-6 bg-card border border-border rounded-bento p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-fg">Knowledge Graph</h3>
            <button
              onClick={() => setShowGraphPanel(false)}
              className="p-1 rounded hover:bg-border/40 text-fg-muted transition-colors"
            >
              <X size={14} />
            </button>
          </div>
          <GraphStatusCard kb={kb} onRefresh={refetch} onToast={addToast} />
        </div>
      )}

      {/* Inline ChunkViewer khi bấm Eye */}
      {viewChunksDoc && (
        <div className="mb-6 bg-card border border-border rounded-bento p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-fg">Chunks — {viewChunksDoc.title}</h3>
            <Button size="sm" variant="ghost" onClick={() => setViewChunksDoc(null)}>
              <X size={14} /> Đóng
            </Button>
          </div>
          <ChunkViewer docId={viewChunksDoc.id} docTitle={viewChunksDoc.title} />
        </div>
      )}

      {/* Document table */}
      <DocumentTable
        kbSlug={slug}
        onViewChunks={(doc) => {
          setViewChunksDoc((prev) => (prev?.id === doc.id ? null : doc))
        }}
        onSelectDoc={handleSelectDoc}
        selectedDocId={selectedDoc?.id}
        onAdd={() => setShowUpload(true)}
        refreshKey={refreshKey}
        onToast={addToast}
      />

      {/* Document preview side panel */}
      <DocumentPreviewPanel
        document={selectedDoc}
        onClose={() => setSelectedDoc(null)}
      />

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

