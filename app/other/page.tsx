'use client'

import { submitMessage, deleteAllMessages } from '../actions'
import { useState } from 'react'

export const runtime = 'edge'

export default function OtherPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(formData: FormData) {
    setLoading(true)
    try {
      const response = await submitMessage(formData)
      setResult(JSON.stringify(response, null, 2))
    } catch (error) {
      setResult(`Error: ${error}`)
    }
    setLoading(false)
  }

  async function handleDelete() {
    setLoading(true)
    try {
      const response = await deleteAllMessages()
      setResult(JSON.stringify(response, null, 2))
    } catch (error) {
      setResult(`Error: ${error}`)
    }
    setLoading(false)
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Other Page - Action Test</h1>
      <p>This page calls the same actions from a different route context.</p>
      <p>This is used to test action forwarding behavior.</p>
      
      <hr style={{ margin: '2rem 0' }} />
      
      <form action={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="message">Message:</label>
          <input 
            type="text" 
            id="message" 
            name="message" 
            defaultValue="Test from /other page"
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{ padding: '0.5rem 1rem', marginRight: '1rem' }}
        >
          {loading ? 'Loading...' : 'Submit Message'}
        </button>
      </form>
      
      <button 
        onClick={handleDelete}
        disabled={loading}
        style={{ padding: '0.5rem 1rem', marginTop: '1rem', backgroundColor: '#ff4444', color: 'white', border: 'none' }}
      >
        Delete All Messages
      </button>
      
      {result && (
        <pre style={{ 
          marginTop: '2rem', 
          padding: '1rem', 
          backgroundColor: '#f5f5f5', 
          borderRadius: '4px',
          overflow: 'auto'
        }}>
          {result}
        </pre>
      )}
      
      <hr style={{ margin: '2rem 0' }} />
      <p><a href="/">← Back to Home</a></p>
    </div>
  )
}
