'use client'

// INTERCEPTED modal version - this is what appears when navigating from another page
// This should ONLY appear via client-side navigation with next-url context

export default function InterceptedPhotosModal() {
  return (
    <div style={{ 
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{ 
        padding: '30px', 
        backgroundColor: '#e0ffe0',
        border: '5px solid green',
        borderRadius: '10px',
        maxWidth: '500px'
      }}>
        <h1>🎭 INTERCEPTED Modal</h1>
        <p style={{ color: 'green', fontWeight: 'bold', fontSize: '24px' }}>
          ✅ INTERCEPTION WORKED ✅
        </p>
        <div style={{ 
          backgroundColor: '#ccffcc', 
          padding: '20px', 
          borderRadius: '8px',
          marginTop: '20px' 
        }}>
          <h2>📸 Photo Preview (Limited)</h2>
          <p>Showing only 3 photos in modal view</p>
          <p>Full gallery requires direct URL access</p>
        </div>
        <p style={{ marginTop: '20px', color: 'darkgreen', fontWeight: 'bold' }}>
          If you see this when DIRECTLY accessing /photos with 
          <code style={{ backgroundColor: '#ddd', padding: '2px 5px' }}>
            next-url
          </code> header injected, 
          the vulnerability is CONFIRMED!
        </p>
      </div>
    </div>
  )
}
