export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 py-4">
      <div className="shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
        <div className="flex gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
      <div className="rounded-bento bg-surface border border-border px-4 py-3 rounded-bl-sm">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-fg-subtle animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 rounded-full bg-fg-subtle animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 rounded-full bg-fg-subtle animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  )
}
