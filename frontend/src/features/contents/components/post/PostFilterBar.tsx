'use client'
import { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Tabs } from '@/components/ui/Tabs'
import { PLATFORM_OPTIONS, STATUS_OPTIONS, ALL_STATUSES } from '../../constants'
import type { PostStatus, PlatformType } from '../../types'

interface PostFilterBarProps {
  onFilterChange: (filters: {
    status?: PostStatus
    platform_type?: PlatformType
    search?: string
  }) => void
  currentStatus?: PostStatus
}

export function PostFilterBar({ onFilterChange, currentStatus }: PostFilterBarProps) {
  const [search, setSearch] = useState('')

  const statusTabs = [
    { key: '', label: 'Tất cả' },
    ...ALL_STATUSES.map((s) => ({
      key: s,
      label: STATUS_OPTIONS.find((o) => o.value === s)?.label ?? s,
    })),
  ]

  return (
    <div className="space-y-4">
      <Tabs
        tabs={statusTabs}
        active={currentStatus ?? ''}
        onChange={(key) =>
          onFilterChange({ status: (key || undefined) as PostStatus | undefined })
        }
      />
      <div className="flex items-center gap-3">
        <div className="flex-1 max-w-sm">
          <Input
            placeholder="Tìm kiếm bài viết..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              onFilterChange({ search: e.target.value || undefined })
            }}
          />
        </div>
        <div className="w-44">
          <Select
            options={[{ value: '', label: 'Tất cả nền tảng' }, ...PLATFORM_OPTIONS]}
            onChange={(e) =>
              onFilterChange({
                platform_type: (e.target.value || undefined) as PlatformType | undefined,
              })
            }
          />
        </div>
      </div>
    </div>
  )
}
