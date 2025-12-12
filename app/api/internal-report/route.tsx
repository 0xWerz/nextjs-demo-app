import { ImageResponse } from 'next/og'
 
// Route: /api/internal-report/route.tsx
// This simulates an internal admin report that renders as an image
// Contains sensitive information that should not be exposed

export async function GET() {
  // Simulate reading secrets from environment or database
  const secrets = {
    dbPassword: process.env.DATABASE_PASSWORD || 'prod_password_12345',
    apiKey: process.env.API_SECRET_KEY || 'sk_live_1234567890abcdef',
    adminToken: 'admin_jwt_eyJhbGciOiJIUzI1NiJ9',
    internalUrl: 'http://10.0.0.5:5432/production',
  }

  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 20,
          color: 'white',
          background: '#1a1a1a',
          width: '100%',
          height: '100%',
          padding: '50px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <h1 style={{ fontSize: 40, marginBottom: 30 }}>🔐 Internal Admin Report</h1>
        <p>Database Password: {secrets.dbPassword}</p>
        <p>API Key: {secrets.apiKey}</p>
        <p>Admin Token: {secrets.adminToken}</p>
        <p>Internal URL: {secrets.internalUrl}</p>
        <p style={{ marginTop: 30, color: '#888' }}>
          Generated: {new Date().toISOString()}
        </p>
      </div>
    ),
    {
      width: 800,
      height: 400,
    }
  )
}
