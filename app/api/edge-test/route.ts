import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Force Edge runtime
export const runtime = 'edge'

export async function GET(request: NextRequest) {
  // Log all headers for debugging
  const headers: Record<string, string> = {}
  request.headers.forEach((value, key) => {
    headers[key] = value
  })

  // Check for internal headers that should have been filtered
  const internalHeaders = {
    'x-middleware-rewrite': request.headers.get('x-middleware-rewrite'),
    'x-middleware-redirect': request.headers.get('x-middleware-redirect'),
    'x-middleware-set-cookie': request.headers.get('x-middleware-set-cookie'),
    'x-middleware-skip': request.headers.get('x-middleware-skip'),
    'x-matched-path': request.headers.get('x-matched-path'),
  }

  return NextResponse.json({
    message: 'Edge Runtime Header Test',
    runtime: 'edge',
    internalHeaders,
    allHeaders: headers,
  })
}
