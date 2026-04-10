'use client'
import { useTheme } from '@/hooks/useTheme'
import { Moon, Sun } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ThemeToggleProps {
  className?: string
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme, mounted } = useTheme()

  if (!mounted) {
    return <div className={cn('w-9 h-9', className)} />
  }

  return (
    <button
      onClick={toggleTheme}
      aria-label={theme === 'light' ? 'Bật dark mode' : 'Bật light mode'}
      className={cn(
        'w-9 h-9 flex items-center justify-center rounded-bento',
        'bg-surface border border-border text-fg-muted hover:text-fg',
        'hover:bg-border/40 transition-colors',
        className
      )}
    >
      {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
    </button>
  )
}
