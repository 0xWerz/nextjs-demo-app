'use client'

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
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Edge Runtime Page (/other)</h1>
        <p className="text-gray-600">This page runs on Edge and forwards actions to Node.</p>
      </div>

      <div className={`p-4 border rounded ${user ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
        <h2 className="text-xl font-bold mb-2">👤 User Session</h2>
        {user ? (
          <div>
            <p className="text-green-700 font-mono">Logged In as: {user}</p>
            <p className="text-xs text-green-600 mt-1">Secret: {secret}</p>
          </div>
        ) : (
          <p className="text-red-700">Not Logged In. <a href="/login" className="underline font-bold">Go to /login</a></p>
        )}
      </div>

      <section className="p-4 border rounded">
        <h2 className="text-xl font-semibold mb-4">Submit Message (Server Action)</h2>
        <form action={handleSubmit} className="space-y-4">
          <input 
            type="text" 
            name="message" 
            placeholder="Enter message..."
            className="w-full p-2 border rounded text-black"
          />
          <button 
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Submit Message'}
          </button>
        </form>
      </section>

      <section className="p-4 border rounded">
        <h2 className="text-xl font-semibold mb-4">Delete All Messages</h2>
        <button 
          onClick={handleDelete}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          disabled={loading}
        >
          {loading ? 'Deleting...' : 'Delete All Messages'}
        </button>
      </section>

      <section className="p-4 border rounded bg-gray-100">
        <h2 className="text-xl font-semibold mb-4 text-black">Last Result:</h2>
        <pre className="bg-white p-2 rounded text-sm overflow-auto text-black">
          {result || 'No action executed yet'}
        </pre>
      </section>
      
      <p><a href="/" className="text-blue-600 hover:underline">← Back to Home</a></p>
    </div>
  )
}
