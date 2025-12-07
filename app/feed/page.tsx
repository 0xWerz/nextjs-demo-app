'use client'

// Feed page - the "source" for interception
export default function FeedPage() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>📰 Feed Page</h1>
      <p>This is the feed. Click the link below to see interception in action.</p>
      <a 
        href="/photos" 
        style={{ 
          color: 'blue', 
          textDecoration: 'underline',
          display: 'block',
          marginTop: '20px' 
        }}
      >
        View Photos (should show modal when coming from feed)
      </a>
    </div>
  )
}
