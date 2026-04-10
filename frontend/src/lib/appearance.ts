import type { AppearanceConfig, ColorGroups } from '@/types/appearance'

/**
 * Server-side fetch — uses INTERNAL_API_URL to avoid internet round-trip.
 * Tagged with 'appearance' for on-demand revalidation.
 */
export async function fetchAppearanceConfig(): Promise<AppearanceConfig | null> {
  const url = `${process.env.INTERNAL_API_URL}/api/v1/appearance/config/`
  try {
    const res = await fetch(url, {
      next: { tags: ['appearance'], revalidate: 3600 },
    })
    if (!res.ok) return null
    const json = await res.json()
    return (json.data as AppearanceConfig) ?? null
  } catch {
    return null
  }
}

/**
 * Build CSS custom properties string from grouped color tokens.
 * Example: buildCssVars(config.colors.light, ':root')
 */
export function buildCssVars(tokens: ColorGroups, selector: string): string {
  const lines = Object.values(tokens)
    .flatMap((group) => group)
    .map((token) => `  --color-${token.key}: ${token.value};`)
  return `${selector} {\n${lines.join('\n')}\n}`
}
