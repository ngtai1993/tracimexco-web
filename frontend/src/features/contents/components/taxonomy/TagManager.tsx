'use client'
import { useState } from 'react'
import { Plus, Tag as TagIcon } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { EmptyState } from '@/components/ui/EmptyState'
import { Spinner } from '@/components/ui/Spinner'
import { useTags } from '../../hooks'

export function TagManager() {
  const { tags, loading, create } = useTags()
  const [newTag, setNewTag] = useState('')
  const [creating, setCreating] = useState(false)

  const handleCreate = async () => {
    if (!newTag.trim()) return
    setCreating(true)
    await create(newTag.trim())
    setNewTag('')
    setCreating(false)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 max-w-sm">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Nhập tên tag mới..."
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
        </div>
        <Button size="sm" onClick={handleCreate} loading={creating} disabled={!newTag.trim()}>
          <Plus size={14} />
          Thêm tag
        </Button>
      </div>

      {tags.length === 0 ? (
        <EmptyState title="Chưa có tag nào" description="Thêm tag đầu tiên ở trên." />
      ) : (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface border border-border text-sm text-fg"
            >
              <TagIcon size={13} className="text-fg-muted" />
              {tag.name}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
