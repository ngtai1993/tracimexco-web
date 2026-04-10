'use client'
import { AnalyticsSummaryCards } from '@/features/contents/components/analytics/AnalyticsSummaryCards'
import { PostsOverTimeChart } from '@/features/contents/components/analytics/PostsOverTimeChart'

export default function ContentsAnalyticsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-fg">Thống kê nội dung</h1>
        <p className="text-sm text-fg-muted mt-1">Tổng quan và biểu đồ bài viết</p>
      </div>

      <div className="space-y-6">
        <AnalyticsSummaryCards />
        <PostsOverTimeChart />
      </div>
    </div>
  )
}
