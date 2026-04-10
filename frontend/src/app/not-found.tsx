import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-dvh bg-bg flex items-center justify-center px-4">
      <div className="text-center">
        <p className="text-8xl font-bold gradient-text mb-4">404</p>
        <h1 className="text-2xl font-semibold text-fg mb-2">
          Không tìm thấy trang
        </h1>
        <p className="text-fg-muted mb-8">
          Trang bạn đang tìm kiếm không tồn tại hoặc đã bị xóa.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-bento bg-primary text-primary-fg font-medium hover:bg-primary-hover transition-colors"
        >
          Về trang chủ
        </Link>
      </div>
    </div>
  )
}
