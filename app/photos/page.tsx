'use client'

// Full photos page - shows SENSITIVE DATA
// This should NOT be accessible via interception route injection

export default function PhotosPage() {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0' }}>
      <h1>📷 Full Photos Page</h1>
      <p style={{ color: 'red', fontWeight: 'bold' }}>
        ⚠️ THIS IS THE FULL PAGE - NOT INTERCEPTED ⚠️
      </p>
      <div style={{ 
        backgroundColor: '#ffcccc', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px' 
      }}>
        <h2>🔒 Sensitive Photo Data</h2>
        <p>Secret API Key: sk-1234567890abcdef</p>
        <p>User Email: admin@company.com</p>
        <p>Photo Count: 1,337 private photos</p>
      </div>
      <p style={{ marginTop: '20px' }}>
        This page contains full data. If you see this via the next-url header
        injection, the vulnerability is NOT present.
      </p>
    </div>
  )
}
