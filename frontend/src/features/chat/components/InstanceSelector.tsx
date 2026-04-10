'use client'
import Link from 'next/link'
import { Bot } from 'lucide-react'
import { useInstances } from '@/features/rag/hooks'

interface InstanceSelectorProps {
  currentSlug?: string
}

export function InstanceSelector({ currentSlug }: InstanceSelectorProps) {
  const { instances, loading } = useInstances()

  const publicInstances = instances.filter(i => i.is_active)

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="rounded-bento border border-border bg-card p-5 animate-pulse h-28" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {publicInstances.map((inst) => (
        <Link
          key={inst.slug}
          href={`/dashboard/chat/${inst.slug}`}
          className={`group block rounded-bento border p-5 transition-all duration-200 ${
            currentSlug === inst.slug
              ? 'border-primary bg-primary/5'
              : 'border-border bg-card hover:border-primary/40 hover:shadow-lg'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-fg group-hover:text-primary transition-colors">
                {inst.name}
              </h3>
              <p className="text-[10px] text-fg-subtle">{inst.provider_name}</p>
            </div>
          </div>
          {inst.description && (
            <p className="text-xs text-fg-muted line-clamp-2">{inst.description}</p>
          )}
        </Link>
      ))}
    </div>
  )
}
