'use client'
import { CategoryManager } from '@/features/contents/components/taxonomy/CategoryManager'

export default function CategoriesPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg">Quản lý danh mục</h1>
        <p className="text-sm text-fg-muted mt-1">Tạo và sắp xếp cây danh mục cho bài viết</p>
      </div>

      <CategoryManager />
    </div>
  )
}
