export default function AppearanceLoading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 rounded bg-surface" />
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 rounded-bento bg-surface" />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="h-48 rounded-bento bg-surface" />
        <div className="h-48 rounded-bento bg-surface" />
      </div>
    </div>
  )
}
