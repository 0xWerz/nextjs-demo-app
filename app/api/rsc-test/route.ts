import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This route tests RSC header handling for cache poisoning research
export async function GET(request: NextRequest) {
  // Extract all RSC-related headers
  const rscHeaders = {
    'rsc': request.headers.get('rsc'),
    'next-router-state-tree': request.headers.get('next-router-state-tree'),
    'next-router-prefetch': request.headers.get('next-router-prefetch'),
    'next-url': request.headers.get('next-url'),
  }
  
  // Check the _rsc query parameter (cache busting hash)
  const url = new URL(request.url)
  const rscHash = url.searchParams.get('_rsc')
  
  return NextResponse.json({
    message: 'RSC Header Test',
    rscHeaders,
    rscHash,
    timestamp: new Date().toISOString(),
    // This response could be cached by CDN
    cacheTest: 'If this value changes per request with same URL, caching is working correctly'
  }, {
    headers: {
      // Simulate a cacheable response
      'Cache-Control': 'public, max-age=3600',
    }
  })
}
