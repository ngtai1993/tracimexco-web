export interface ColorToken {
  key: string
  value: string
  name: string
}

export interface ColorGroups {
  brand: ColorToken[]
  semantic: ColorToken[]
  neutral: ColorToken[]
  [group: string]: ColorToken[]
}

export interface MediaAssetRef {
  url: string | null
  alt: string
}

export interface AppearanceConfig {
  colors: {
    light: ColorGroups
    dark: ColorGroups
  }
  media: Record<string, MediaAssetRef | null>
}
