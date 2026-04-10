import { MessageSquare } from 'lucide-react'

interface EmptyChatProps {
  instanceName?: string
}

export function EmptyChat({ instanceName }: EmptyChatProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center p-8">
      <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
        <MessageSquare size={28} className="text-primary" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-fg mb-1">
          {instanceName ? `Chat với ${instanceName}` : 'Bắt đầu trò chuyện'}
        </h3>
        <p className="text-sm text-fg-muted max-w-md">
          Hãy đặt câu hỏi để bắt đầu. AI sẽ tìm kiếm thông tin từ knowledge base
          và trả lời bạn.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2 mt-2">
        {[
          'Tóm tắt tài liệu',
          'Tìm thông tin về...',
          'So sánh giữa...',
        ].map((suggestion) => (
          <span
            key={suggestion}
            className="text-xs px-3 py-1.5 rounded-full border border-border text-fg-muted hover:border-primary/40 hover:text-primary cursor-default transition-colors"
          >
            {suggestion}
          </span>
        ))}
      </div>
    </div>
  )
}
