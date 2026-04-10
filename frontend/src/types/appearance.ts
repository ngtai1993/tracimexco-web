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

export interface AppearanceConfig {
  colors: {
    light: ColorGroups
    dark: ColorGroups
  }
  media: Record<string, string | null>
}
