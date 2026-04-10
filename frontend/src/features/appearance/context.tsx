'use client'
import { createContext, useContext } from 'react'
import type { AppearanceConfig } from '@/types/appearance'

const AppearanceContext = createContext<AppearanceConfig | null>(null)

export function AppearanceProvider({
  config,
  children,
}: {
  config: AppearanceConfig | null
  children: React.ReactNode
}) {
  return (
    <AppearanceContext.Provider value={config}>
      {children}
    </AppearanceContext.Provider>
  )
}

export function useAppearanceContext() {
  return useContext(AppearanceContext)
}
