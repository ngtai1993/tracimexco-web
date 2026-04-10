'use client'
import Link from 'next/link'
import { useState } from 'react'
import { Palette, ImageIcon, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { PalettePanel } from '@/features/appearance/admin/components/PalettePanel'
import { useTokens } from '@/features/appearance/admin/hooks'
import { useAssets } from '@/features/appearance/admin/hooks'
import { revalidateAppearanceCache } from '@/features/appearance/admin/api'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/ui/Toast'

export default function AppearanceOverviewPage() {
  const { tokens, loading: tokensLoading } = useTokens({ include_inactive: false })
  const { assets, loading: assetsLoading } = useAssets({ include_inactive: false })
  const [reloading, setReloading] = useState(false)
  const { toasts, addToast, removeToast } = useToast()

  const handleReload = async () => {
    setReloading(true)
    await revalidateAppearanceCache()
    setReloading(false)
    addToast('Cache đã được xóa. Trang web sẽ hiển thị màu mới.', 'success')
  }

  const lightCount = tokens.filter((t) => t.mode === 'light').length
  const darkCount = tokens.filter((t) => t.mode === 'dark').length

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-fg">Appearance</h1>
          <p className="text-sm text-fg-muted mt-1">Quản lý màu sắc và media của hệ thống</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleReload} loading={reloading}>
          <RefreshCw size={15} />
          Reload cache trang web
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-surface border border-border rounded-bento p-4">
          <p className="text-xs text-fg-muted mb-1">Token light</p>
          <p className="text-2xl font-semibold text-fg">{tokensLoading ? '—' : lightCount}</p>
        </div>
        <div className="bg-surface border border-border rounded-bento p-4">
          <p className="text-xs text-fg-muted mb-1">Token dark</p>
          <p className="text-2xl font-semibold text-fg">{tokensLoading ? '—' : darkCount}</p>
        </div>
        <div className="bg-surface border border-border rounded-bento p-4">
          <p className="text-xs text-fg-muted mb-1">Media assets</p>
          <p className="text-2xl font-semibold text-fg">{assetsLoading ? '—' : assets.length}</p>
        </div>
      </div>

      {/* Palette preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-surface border border-border rounded-bento p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-fg flex items-center gap-2">
              <Palette size={16} /> Palette — Light
            </h2>
            <Link href="/dashboard/appearance/tokens" className="text-xs text-primary hover:underline">
              Quản lý →
            </Link>
          </div>
          {tokensLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-6 rounded bg-bg-subtle animate-pulse" />
              ))}
            </div>
          ) : (
            <PalettePanel tokens={tokens} mode="light" />
          )}
        </div>

        <div className="bg-surface border border-border rounded-bento p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-fg flex items-center gap-2">
              <Palette size={16} /> Palette — Dark
            </h2>
            <Link href="/dashboard/appearance/tokens" className="text-xs text-primary hover:underline">
              Quản lý →
            </Link>
          </div>
          {tokensLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-6 rounded bg-bg-subtle animate-pulse" />
              ))}
            </div>
          ) : (
            <PalettePanel tokens={tokens} mode="dark" />
          )}
        </div>
      </div>

      {/* Media assets quick link */}
      <div className="bg-surface border border-border rounded-bento p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-fg flex items-center gap-2">
            <ImageIcon size={16} /> Media Assets
          </h2>
          <Link href="/dashboard/appearance/assets" className="text-xs text-primary hover:underline">
            Quản lý →
          </Link>
        </div>
        {assetsLoading ? (
          <div className="flex gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="w-20 h-12 rounded-lg bg-bg-subtle animate-pulse" />
            ))}
          </div>
        ) : assets.length === 0 ? (
          <p className="text-sm text-fg-subtle">Chưa có asset nào</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {assets.map((a) => (
              <div key={a.id} className="flex flex-col items-center gap-1">
                <div className="w-20 h-12 rounded-lg border border-border bg-bg-subtle flex items-center justify-center overflow-hidden">
                  {a.file_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={a.file_url} alt={a.alt_text || a.name} className="object-contain w-full h-full p-1" />
                  ) : (
                    <ImageIcon size={16} className="text-fg-subtle" />
                  )}
                </div>
                <span className="text-xs text-fg-muted font-mono">{a.key}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
