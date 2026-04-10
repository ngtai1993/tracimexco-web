'use client'
import { useEffect, useState, useCallback } from 'react'

type Theme = 'light' | 'dark'
const STORAGE_KEY = 'theme'

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>('light')
  const [mounted, setMounted] = useState(false)

  const apply = useCallback((next: Theme) => {
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem(STORAGE_KEY, next)
    setThemeState(next)
  }, [])

  useEffect(() => {
    setMounted(true)
    const saved = localStorage.getItem(STORAGE_KEY) as Theme | null
    const preferred: Theme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
    apply(saved ?? preferred)
  }, [apply])

  const toggleTheme = useCallback(() => {
    apply(theme === 'light' ? 'dark' : 'light')
  }, [theme, apply])

  return { theme, toggleTheme, setTheme: apply, mounted }
}
