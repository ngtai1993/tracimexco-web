import Image from 'next/image'
import Link from 'next/link'

interface AppLogoProps {
  src?: string | null
  alt?: string
  height?: number
}

export function AppLogo({ src, alt = 'Logo', height = 36 }: AppLogoProps) {
  return (
    <Link href="/" className="flex items-center gap-2 shrink-0">
      {src ? (
        <Image
          src={src}
          alt={alt}
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
