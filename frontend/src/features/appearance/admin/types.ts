export interface ColorTokenAdmin {
  id: string
  name: string
  key: string
  mode: 'light' | 'dark'
  value: string
  group: 'brand' | 'semantic' | 'neutral' | 'custom'
  description: string
  order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MediaAssetAdmin {
  id: string
  name: string
  key: string
  file_url: string | null
  alt_text: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateTokenInput {
  name: string
  key: string
  mode: 'light' | 'dark'
  value: string
  group: 'brand' | 'semantic' | 'neutral' | 'custom'
  description?: string
  order?: number
  is_active?: boolean
}

export type UpdateTokenInput = Partial<CreateTokenInput>

export interface CreateAssetInput {
  name: string
  key: string
  alt_text?: string
  description?: string
  is_active?: boolean
}

export type UpdateAssetInput = Partial<CreateAssetInput>
