import { ImageResponse } from 'next/og'

// This endpoint should be protected by middleware requiring Authorization header
// Testing if SSRF via /_next/image bypasses this protection

export async function GET(request: Request) {
  const authHeader = request.headers.get('authorization')
  
  // Check auth
  if (!authHeader || authHeader !== 'Bearer secret-token') {
    return new Response('Unauthorized', { status: 401 })
  }
  
  // If authorized, return a "secret" image
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 40,
          background: 'red',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
        }}
      >
        SECRET IMAGE - AUTH BYPASSED!
      </div>
    ),
    {
      width: 400,
      height: 200,
    }
  )
}
