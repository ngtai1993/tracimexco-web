'use client'
import { useState } from 'react'
import { X } from 'lucide-react'
import type { ImageResult } from '../types'

interface ImageGalleryProps {
  images: ImageResult[]
}

export function ImageGallery({ images }: ImageGalleryProps) {
  const [selected, setSelected] = useState<ImageResult | null>(null)

  if (images.length === 0) return null

  return (
    <>
      <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 gap-2">
        {images.map((img) => (
          <button
            key={img.id}
            onClick={() => setSelected(img)}
            className="group relative rounded-md overflow-hidden border border-border hover:border-primary/40 transition-colors"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={img.url}
              alt={img.caption}
              className="w-full h-24 object-cover"
            />
            {img.caption && (
              <div className="absolute bottom-0 inset-x-0 bg-black/60 px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="text-[10px] text-white truncate">{img.caption}</p>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Lightbox */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
          onClick={() => setSelected(null)}
        >
          <div className="relative max-w-3xl max-h-[80vh] m-4" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setSelected(null)}
              className="absolute -top-3 -right-3 p-1.5 rounded-full bg-surface text-fg hover:bg-primary hover:text-white transition-colors z-10"
            >
              <X size={16} />
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={selected.url}
              alt={selected.caption}
              className="rounded-bento max-h-[80vh] object-contain"
            />
            {selected.caption && (
              <p className="text-sm text-white text-center mt-2">{selected.caption}</p>
            )}
          </div>
        </div>
      )}
    </>
  )
}
