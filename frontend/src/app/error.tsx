'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-dvh bg-bg flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <p className="text-6xl font-bold gradient-text mb-4">Lỗi</p>
        <h1 className="text-xl font-semibold text-fg mb-2">Có lỗi xảy ra</h1>
        <p className="text-fg-muted mb-8 text-sm">
          {error.message || 'Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.'}
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 rounded-bento bg-primary text-primary-fg font-medium hover:bg-primary-hover transition-colors"
        >
          Thử lại
        </button>
      </div>
    </div>
  )
}
