import { ColorSwatch } from '@/components/ui/ColorSwatch'
import type { ColorTokenAdmin } from '../types'

interface PalettePanelProps {
  tokens: ColorTokenAdmin[]
  mode: 'light' | 'dark'
}

const groupOrder = ['brand', 'semantic', 'neutral', 'custom']

function groupBy<T>(items: T[], key: keyof T): Record<string, T[]> {
  return items.reduce<Record<string, T[]>>((acc, item) => {
    const k = String(item[key])
    ;(acc[k] = acc[k] ?? []).push(item)
    return acc
  }, {})
}

export function PalettePanel({ tokens, mode }: PalettePanelProps) {
  const filtered = tokens.filter((t) => t.mode === mode && t.is_active)
  const grouped = groupBy(filtered, 'group')

  return (
    <div className="space-y-4">
      {groupOrder.map((group) => {
        const items = grouped[group]
        if (!items?.length) return null
        return (
          <div key={group}>
            <p className="text-xs font-medium text-fg-muted uppercase tracking-wide mb-2">{group}</p>
            <div className="flex flex-wrap gap-2">
              {items.map((t) => (
                <div key={t.id} className="flex items-center gap-1.5" title={`${t.key}: ${t.value}`}>
                  <ColorSwatch value={t.value} size="md" />
                  <span className="text-xs text-fg-muted font-mono">{t.key}</span>
                </div>
              ))}
            </div>
          </div>
        )
      })}
      {filtered.length === 0 && (
        <p className="text-sm text-fg-subtle">Chưa có token nào cho mode {mode}</p>
      )}
    </div>
  )
}
