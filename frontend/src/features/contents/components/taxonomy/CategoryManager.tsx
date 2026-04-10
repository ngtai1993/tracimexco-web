'use client'
import { useState } from 'react'
import { ChevronRight, ChevronDown, Folder, FolderOpen, Plus, Trash2, Pencil } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { EmptyState } from '@/components/ui/EmptyState'
import { Spinner } from '@/components/ui/Spinner'
import { useCategories } from '../../hooks'
import type { Category } from '../../types'

interface CategoryTreeNode extends Category {
  children: CategoryTreeNode[]
}

function buildTree(categories: Category[]): CategoryTreeNode[] {
  const map = new Map<string, CategoryTreeNode>()
  const roots: CategoryTreeNode[] = []

  for (const cat of categories) {
    map.set(cat.id, { ...cat, children: [] })
  }

  for (const cat of categories) {
    const node = map.get(cat.id)!
    if (cat.parent && map.has(cat.parent)) {
      map.get(cat.parent)!.children.push(node)
    } else {
      roots.push(node)
    }
  }

  return roots
}

export function CategoryManager() {
  const { categories, loading, create, update, remove } = useCategories()
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [showDelete, setShowDelete] = useState<string | null>(null)

  const tree = buildTree(categories)
  const selected = categories.find((c) => c.slug === selectedSlug)

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left — Tree */}
      <div className="lg:col-span-1 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-fg">Danh mục</h3>
          <Button size="sm" variant="outline" onClick={() => setShowCreate(true)}>
            <Plus size={14} />
            Thêm
          </Button>
        </div>

        {tree.length === 0 ? (
          <EmptyState title="Chưa có danh mục" description="Tạo danh mục đầu tiên." />
        ) : (
          <div className="rounded-bento border border-border bg-card p-2">
            {tree.map((node) => (
              <TreeItem
                key={node.id}
                node={node}
                selected={selectedSlug}
                onSelect={setSelectedSlug}
                onDelete={setShowDelete}
              />
            ))}
          </div>
        )}
      </div>

      {/* Right — Edit Panel */}
      <div className="lg:col-span-2">
        {selected ? (
          <CategoryEditPanel
            category={selected}
            categories={categories}
            onSave={async (data) => {
              await update(selected.slug, data)
            }}
          />
        ) : (
          <div className="rounded-bento border border-border bg-card p-8 text-center text-fg-muted text-sm">
            Chọn một danh mục bên trái để chỉnh sửa.
          </div>
        )}
      </div>

      {/* Create Modal */}
      <CategoryCreateModal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        categories={categories}
        onCreate={async (data) => {
          await create(data)
          setShowCreate(false)
        }}
      />

      {/* Delete Confirm */}
      <ConfirmDialog
        open={!!showDelete}
        onClose={() => setShowDelete(null)}
        onConfirm={async () => {
          if (showDelete) {
            await remove(showDelete)
            if (selectedSlug === showDelete) setSelectedSlug(null)
            setShowDelete(null)
          }
        }}
        title="Xóa danh mục"
        message="Bạn có chắc muốn xóa danh mục này?"
        confirmLabel="Xóa"
      />
    </div>
  )
}

// ── Tree Item ─────────────────────────────────────────────────

interface TreeItemProps {
  node: CategoryTreeNode
  selected: string | null
  onSelect: (slug: string) => void
  onDelete: (slug: string) => void
  depth?: number
}

function TreeItem({ node, selected, onSelect, onDelete, depth = 0 }: TreeItemProps) {
  const [expanded, setExpanded] = useState(true)
  const hasChildren = node.children.length > 0
  const isSelected = selected === node.slug

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer text-sm transition-colors',
          isSelected ? 'bg-primary/10 text-primary' : 'text-fg hover:bg-surface'
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        <button
          onClick={() => hasChildren && setExpanded(!expanded)}
          className={cn('shrink-0', !hasChildren && 'invisible')}
        >
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        {expanded && hasChildren ? <FolderOpen size={15} /> : <Folder size={15} />}
        <span className="flex-1 truncate" onClick={() => onSelect(node.slug)}>
          {node.name}
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(node.slug) }}
          className="opacity-0 group-hover:opacity-100 hover:text-danger p-0.5"
        >
          <Trash2 size={13} />
        </button>
      </div>
      {expanded && node.children.map((child) => (
        <TreeItem
          key={child.id}
          node={child}
          selected={selected}
          onSelect={onSelect}
          onDelete={onDelete}
          depth={depth + 1}
        />
      ))}
    </div>
  )
}

// ── Category Edit Panel ───────────────────────────────────────

interface CategoryEditPanelProps {
  category: Category
  categories: Category[]
  onSave: (data: Partial<Category>) => void
}

function CategoryEditPanel({ category, categories, onSave }: CategoryEditPanelProps) {
  const [name, setName] = useState(category.name)
  const [description, setDescription] = useState(category.description)
  const [parent, setParent] = useState(category.parent ?? '')
  const [order, setOrder] = useState(category.order)
  const [saving, setSaving] = useState(false)

  // Reset when category changes
  useState(() => {
    setName(category.name)
    setDescription(category.description)
    setParent(category.parent ?? '')
    setOrder(category.order)
  })

  const parentOptions = [
    { value: '', label: 'Không có cha (Root)' },
    ...categories
      .filter((c) => c.id !== category.id)
      .map((c) => ({ value: c.id, label: c.name })),
  ]

  const handleSave = async () => {
    setSaving(true)
    await onSave({ name, description, parent: parent || null, order })
    setSaving(false)
  }

  return (
    <div className="rounded-bento border border-border bg-card p-5 space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Pencil size={16} className="text-fg-muted" />
        <h3 className="text-base font-semibold text-fg">Chỉnh sửa: {category.name}</h3>
      </div>
      <Input label="Tên" value={name} onChange={(e) => setName(e.target.value)} />
      <Textarea label="Mô tả" value={description} onChange={(e) => setDescription(e.target.value)} />
      <Select
        label="Danh mục cha"
        options={parentOptions}
        value={parent}
        onChange={(e) => setParent(e.target.value)}
      />
      <Input label="Thứ tự" type="number" value={order} onChange={(e) => setOrder(Number(e.target.value))} />
      <div className="flex justify-end">
        <Button size="sm" onClick={handleSave} loading={saving}>
          Lưu
        </Button>
      </div>
    </div>
  )
}

// ── Create Modal ──────────────────────────────────────────────

interface CategoryCreateModalProps {
  open: boolean
  onClose: () => void
  categories: Category[]
  onCreate: (data: { name: string; parent?: string | null; description?: string; order?: number }) => void
}

function CategoryCreateModal({ open, onClose, categories, onCreate }: CategoryCreateModalProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [parent, setParent] = useState('')

  const parentOptions = [
    { value: '', label: 'Không có cha (Root)' },
    ...categories.map((c) => ({ value: c.id, label: c.name })),
  ]

  const handleCreate = () => {
    if (!name.trim()) return
    onCreate({ name: name.trim(), description, parent: parent || null })
    setName('')
    setDescription('')
    setParent('')
  }

  return (
    <Modal open={open} onClose={onClose} title="Tạo danh mục mới">
      <div className="space-y-4">
        <Input label="Tên" value={name} onChange={(e) => setName(e.target.value)} placeholder="Tên danh mục..." />
        <Textarea label="Mô tả" value={description} onChange={(e) => setDescription(e.target.value)} />
        <Select
          label="Danh mục cha"
          options={parentOptions}
          value={parent}
          onChange={(e) => setParent(e.target.value)}
        />
        <div className="flex justify-end gap-2">
          <Button size="sm" variant="ghost" onClick={onClose}>Hủy</Button>
          <Button size="sm" onClick={handleCreate} disabled={!name.trim()}>Tạo</Button>
        </div>
      </div>
    </Modal>
  )
}
