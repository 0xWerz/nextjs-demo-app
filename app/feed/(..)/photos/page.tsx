'use client'

// Intercepted modal version - shows LIMITED/DIFFERENT data
// This is what should appear when navigating FROM /feed TO /photos

export default function InterceptedPhotosModal() {
  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#e0ffe0',
      border: '3px solid green' 
    }}>
      <h1>🎭 INTERCEPTED Modal Version</h1>
      <p style={{ color: 'green', fontWeight: 'bold' }}>
        ✅ THIS IS THE INTERCEPTED ROUTE ✅
      </p>
      <div style={{ 
        backgroundColor: '#ccffcc', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px' 
      }}>
        <h2>📸 Photo Preview (Limited View)</h2>
        <p>Showing: 3 recent photos only</p>
        <p>Full gallery requires direct access</p>
      </div>
      <p style={{ marginTop: '20px', color: 'darkgreen' }}>
        <strong>VULNERABILITY CONFIRMED!</strong> If you see this when directly
        accessing /photos with the next-url header injected, the interception
        route hijacking attack worked!
      </p>
    </div>
  )
}
