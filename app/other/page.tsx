import { submitMessage, deleteAllMessages, getSecretData } from '../actions'
import { useState, useEffect } from 'react'

export const runtime = 'edge'

export default function OtherPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<string | null>(null)
  const [secret, setSecret] = useState<string | null>(null)

  useEffect(() => {
    // Check if we are logged in by trying to fetch secret data
    getSecretData()
      .then(data => {
        setUser(data.user)
        setSecret(data.secret)
      })
      .catch(() => setUser(null))
  }, [])

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
