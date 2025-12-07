import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Protect /photos - require auth header
  if (request.nextUrl.pathname === '/photos') {
    const authHeader = request.headers.get('authorization')
    if (!authHeader || authHeader !== 'Bearer secret-token') {
      console.log('Middleware: Blocking unauthorized access to /photos')
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    console.log('Middleware: Authorized access to /photos')
  }
  return NextResponse.next()
}

export const config = {
  matcher: '/photos',
}
