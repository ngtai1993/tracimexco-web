'use client'
import { cn } from '@/lib/utils'

interface Tab {
  key: string
  label: string
  icon?: React.ReactNode
}

interface TabsProps {
  tabs: Tab[]
  active: string
  onChange: (key: string) => void
  className?: string
}

export function Tabs({ tabs, active, onChange, className }: TabsProps) {
  return (
    <div className={cn('flex gap-1 border-b border-border', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={cn(
            'flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors -mb-px',
            'border-b-2',
            active === tab.key
              ? 'border-primary text-primary'
              : 'border-transparent text-fg-muted hover:text-fg hover:border-border'
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  )
}
