import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const jar = await cookies()
  jar.delete('access_token')

  const referer = request.headers.get('referer')
  const redirectUrl = referer ? new URL('/login', referer) : new URL('/login', 'http://localhost:3000')
  return NextResponse.redirect(redirectUrl)
}