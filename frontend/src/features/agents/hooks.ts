'use client'
import { useState, useEffect, useCallback } from 'react'
import { agentApi } from './api'
import type {
  AgentProvider,
  AgentProviderInput,
  AgentAPIKey,
  AgentAPIKeyInput,
  AgentAPIKeyUpdate,
  AgentConfig,
  AgentConfigInput,
} from './types'

function extractError(err: unknown): string {
  const e = err as { response?: { data?: { message?: string }; status?: number } }
  if (e.response?.status === 401) return 'Phiên đăng nhập đã hết hạn'
  if (e.response?.status === 403) return 'Bạn không có quyền thực hiện thao tác này'
  return e.response?.data?.message ?? 'Đã xảy ra lỗi'
}

// ── Providers ──────────────────────────────────────────

export function useProviders(includeInactive = false) {
  const [providers, setProviders] = useState<AgentProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.listProviders(includeInactive)
      setProviders(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [includeInactive])

  useEffect(() => { fetch() }, [fetch])

  return { providers, loading, error, refetch: fetch }
}

export function useCreateProvider() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = async (data: AgentProviderInput): Promise<AgentProvider | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.createProvider(data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error }
}

export function useUpdateProvider() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = async (slug: string, data: Partial<AgentProviderInput>): Promise<AgentProvider | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.updateProvider(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { update, loading, error }
}

export function useDeleteProvider() {
  const [loading, setLoading] = useState(false)

  const remove = async (slug: string): Promise<boolean> => {
    setLoading(true)
    try {
      await agentApi.deleteProvider(slug)
      return true
    } catch {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { remove, loading }
}

// ── Keys ───────────────────────────────────────────────

export function useKeys(providerSlug: string) {
  const [keys, setKeys] = useState<AgentAPIKey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!providerSlug) return
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.listKeys(providerSlug)
      setKeys(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [providerSlug])

  useEffect(() => { fetch() }, [fetch])

  return { keys, loading, error, refetch: fetch }
}

export function useCreateKey() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = async (slug: string, data: AgentAPIKeyInput): Promise<AgentAPIKey | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.createKey(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error }
}

export function useUpdateKey() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = async (slug: string, keyId: string, data: AgentAPIKeyUpdate): Promise<AgentAPIKey | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.updateKey(slug, keyId, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { update, loading, error }
}

export function useDeleteKey() {
  const [loading, setLoading] = useState(false)

  const remove = async (slug: string, keyId: string): Promise<boolean> => {
    setLoading(true)
    try {
      await agentApi.deleteKey(slug, keyId)
      return true
    } catch {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { remove, loading }
}

// ── Configs ────────────────────────────────────────────

export function useConfigs(providerSlug: string) {
  const [configs, setConfigs] = useState<AgentConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    if (!providerSlug) return
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.listConfigs(providerSlug)
      setConfigs(res.data.data)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }, [providerSlug])

  useEffect(() => { fetch() }, [fetch])

  return { configs, loading, error, refetch: fetch }
}

export function useCreateConfig() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const create = async (slug: string, data: AgentConfigInput): Promise<AgentConfig | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.createConfig(slug, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error }
}

export function useUpdateConfig() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = async (slug: string, configId: string, data: Partial<AgentConfigInput>): Promise<AgentConfig | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await agentApi.updateConfig(slug, configId, data)
      return res.data.data
    } catch (err) {
      setError(extractError(err))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { update, loading, error }
}

export function useDeleteConfig() {
  const [loading, setLoading] = useState(false)

  const remove = async (slug: string, configId: string): Promise<boolean> => {
    setLoading(true)
    try {
      await agentApi.deleteConfig(slug, configId)
      return true
    } catch {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { remove, loading }
}
