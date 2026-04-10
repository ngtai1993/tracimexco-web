import Image from 'next/image'
import Link from 'next/link'
import type { MediaAssetRef } from '@/types/appearance'

interface AppLogoProps {
  asset?: MediaAssetRef | null
  height?: number
}

export function AppLogo({ asset, height = 36 }: AppLogoProps) {
  return (
    <Link href="/" className="flex items-center gap-2 shrink-0">
      {asset?.url ? (
        <Image
          src={asset.url}
          alt={asset.alt || 'Logo'}
          height={height}
          width={height * 4}
          className="object-contain h-9 w-auto"
          priority
        />
      ) : (
        <span className="text-xl font-bold gradient-text tracking-tight">
          App
        </span>
      )}
    </Link>
  )
}
