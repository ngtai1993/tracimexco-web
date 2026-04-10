'use client'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface SliderProps {
  label?: string
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  step?: number
  hint?: string
  className?: string
}

export function Slider({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  hint,
  className,
}: SliderProps) {
  const [localValue, setLocalValue] = useState(value)
  const percentage = ((localValue - min) / (max - min)) * 100

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-fg">{label}</span>
          <span className="text-sm font-mono text-primary">{localValue}</span>
        </div>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={localValue}
        onChange={(e) => {
          const v = Number(e.target.value)
          setLocalValue(v)
        }}
        onMouseUp={() => onChange(localValue)}
        onTouchEnd={() => onChange(localValue)}
        className="w-full h-2 rounded-full appearance-none cursor-pointer bg-border accent-primary"
        style={{
          background: `linear-gradient(to right, var(--color-primary) ${percentage}%, var(--color-border) ${percentage}%)`,
        }}
      />
      {hint && <p className="text-xs text-fg-muted">{hint}</p>}
    </div>
  )
}
