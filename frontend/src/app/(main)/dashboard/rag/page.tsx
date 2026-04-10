'use client'
import { useState } from 'react'
import { Plus, Database, Brain } from 'lucide-react'
import { Modal } from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'
import { Tabs } from '@/components/ui/Tabs'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { ToastContainer } from '@/components/ui/Toast'
import { useToast } from '@/hooks/useToast'
import { InstanceCard, InstanceForm, KBCard, KBForm } from '@/features/rag'
import { useInstances, useKnowledgeBases } from '@/features/rag/hooks'

export default function RAGOverviewPage() {
  const [tab, setTab] = useState('instances')
  const { instances, loading: instLoading, refetch: refetchInst } = useInstances(true)
  const { kbs, loading: kbLoading, refetch: refetchKB } = useKnowledgeBases(true)
  const [showCreateInst, setShowCreateInst] = useState(false)
  const [showCreateKB, setShowCreateKB] = useState(false)
  const { toasts, addToast, removeToast } = useToast()

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">RAG System</h1>
          <p className="text-sm text-fg-muted mt-1">Quản lý RAG instances và knowledge bases</p>
        </div>
        <div className="flex gap-2">
          {tab === 'instances' && (
            <Button size="sm" onClick={() => setShowCreateInst(true)}>
              <Plus size={16} /> Tạo Instance
            </Button>
          )}
          {tab === 'kbs' && (
            <Button size="sm" onClick={() => setShowCreateKB(true)}>
              <Plus size={16} /> Tạo KB
            </Button>
          )}
        </div>
      </div>

      <Tabs
        tabs={[
          { key: 'instances', label: 'RAG Instances', icon: <Brain size={14} /> },
          { key: 'kbs', label: 'Knowledge Bases', icon: <Database size={14} /> },
        ]}
        active={tab}
        onChange={setTab}
        className="mb-6"
      />

      {/* Instances Tab */}
      {tab === 'instances' && (
        instLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : instances.length === 0 ? (
          <EmptyState
            icon={<Brain size={40} strokeWidth={1.5} />}
            title="Chưa có RAG instance nào"
            description="Tạo instance đầu tiên để bắt đầu"
            actionLabel="Tạo Instance"
            onAction={() => setShowCreateInst(true)}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {instances.map((inst) => (
              <InstanceCard key={inst.id} instance={inst} />
            ))}
          </div>
        )
      )}

      {/* KBs Tab */}
      {tab === 'kbs' && (
        kbLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : kbs.length === 0 ? (
          <EmptyState
            icon={<Database size={40} strokeWidth={1.5} />}
            title="Chưa có Knowledge Base nào"
            description="Tạo KB đầu tiên để lưu trữ tài liệu"
            actionLabel="Tạo KB"
            onAction={() => setShowCreateKB(true)}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {kbs.map((kb) => (
              <KBCard key={kb.id} kb={kb} />
            ))}
          </div>
        )
      )}

      {/* Create Instance Modal */}
      <Modal open={showCreateInst} onClose={() => setShowCreateInst(false)} title="Tạo RAG Instance" className="max-w-xl">
        <InstanceForm
          onSuccess={() => { setShowCreateInst(false); refetchInst(); addToast('Đã tạo instance', 'success') }}
          onCancel={() => setShowCreateInst(false)}
        />
      </Modal>

      {/* Create KB Modal */}
      <Modal open={showCreateKB} onClose={() => setShowCreateKB(false)} title="Tạo Knowledge Base" className="max-w-xl">
        <KBForm
          onSuccess={() => { setShowCreateKB(false); refetchKB(); addToast('Đã tạo knowledge base', 'success') }}
          onCancel={() => setShowCreateKB(false)}
        />
      </Modal>
    </>
  )
}
