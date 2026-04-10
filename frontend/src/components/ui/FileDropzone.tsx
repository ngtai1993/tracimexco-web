'use client'
import { useRef, useState } from 'react'
import { UploadCloud, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileDropzoneProps {
  accept?: string
  maxSizeMB?: number
  value?: File | null
  onChange: (file: File | null) => void
  error?: string
  label?: string
}

export function FileDropzone({
  accept = 'image/*',
  maxSizeMB = 5,
  value,
  onChange,
  error,
  label,
}: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [sizeError, setSizeError] = useState<string | null>(null)

  const handleFile = (file: File) => {
    setSizeError(null)
    if (file.size > maxSizeMB * 1024 * 1024) {
      setSizeError(`Kích thước tối đa là ${maxSizeMB}MB`)
      return
    }
    onChange(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const displayError = error ?? sizeError

  return (
    <div className="flex flex-col gap-1.5">
      {label && <span className="text-sm font-medium text-fg">{label}</span>}
      <div
        className={cn(
          'relative flex flex-col items-center justify-center gap-2 rounded-bento border-2 border-dashed p-6',
          'cursor-pointer transition-colors',
          dragging
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50 hover:bg-surface',
          displayError && 'border-danger'
        )}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="sr-only"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />
        {value ? (
          <div className="flex items-center gap-3 w-full">
            <span className="flex-1 text-sm text-fg truncate">{value.name}</span>
            <button
              type="button"
              className="shrink-0 p-1 rounded hover:bg-border/40 text-fg-muted"
              onClick={(e) => { e.stopPropagation(); onChange(null); setSizeError(null) }}
              aria-label="Xóa file"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <>
            <UploadCloud size={28} className="text-fg-muted" />
            <p className="text-sm text-fg-muted text-center">
              Kéo thả file hoặc <span className="text-primary font-medium">chọn file</span>
            </p>
            <p className="text-xs text-fg-subtle">Tối đa {maxSizeMB}MB</p>
          </>
        )}
      </div>
      {displayError && <p className="text-xs text-danger">{displayError}</p>}
    </div>
  )
}
