'use client'
import { Cpu, PlugZap, Wrench, ToggleLeft, ToggleRight, Pencil, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { RAGSkill } from '../types'

interface SkillCardProps {
  skill: RAGSkill
  onEdit?: (skill: RAGSkill) => void
  onDelete?: (skill: RAGSkill) => void
}

const SKILL_META: Record<string, { label: string; icon: React.ComponentType<{ size?: number; className?: string }> }> = {
  builtin: { label: 'Built-in', icon: Cpu },
  api_call: { label: 'API Call', icon: PlugZap },
  custom: { label: 'Custom', icon: Wrench },
}

export function SkillCard({ skill, onEdit, onDelete }: SkillCardProps) {
  const meta = SKILL_META[skill.skill_type] ?? { label: skill.skill_type, icon: Wrench }
  const Icon = meta.icon
  const configCount = Object.keys(skill.config ?? {}).length

  return (
    <article
      className={cn(
        'rounded-bento border border-border bg-card p-5',
        'hover:border-primary/40 hover:shadow-lg transition-all duration-200',
        !skill.is_active && 'opacity-60'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <Icon size={16} className="text-primary shrink-0" />
          <h3 className="text-base font-semibold text-fg truncate">{skill.name}</h3>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {onEdit && (
            <button
              onClick={() => onEdit(skill)}
              className="p-1.5 rounded hover:bg-surface text-fg-muted hover:text-primary transition-colors"
              title="Sửa skill"
            >
              <Pencil size={14} />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(skill)}
              className="p-1.5 rounded hover:bg-danger/10 text-fg-muted hover:text-danger transition-colors"
              title="Xóa skill"
            >
              <Trash2 size={14} />
            </button>
          )}
          {skill.is_active ? (
            <ToggleRight size={20} className="text-success ml-1" />
          ) : (
            <ToggleLeft size={20} className="text-fg-subtle ml-1" />
          )}
        </div>
      </div>

      {skill.description && (
        <p className="text-sm text-fg-muted mb-3 line-clamp-2">{skill.description}</p>
      )}

      <div className="flex items-center gap-2 text-xs text-fg-muted mb-3">
        <span className="px-2 py-0.5 rounded-full bg-border/60">{meta.label}</span>
        <span>•</span>
        <span>{configCount} config keys</span>
      </div>

      <div className="pt-3 border-t border-border/50 text-xs text-fg-subtle">
        slug: {skill.slug}
      </div>
    </article>
  )
}
