'use client'
// Force git update


import { submitMessage, deleteAllMessages, getMessages } from './actions'
import { useState, useEffect } from 'react'

export default function Home() {
  const [result, setResult] = useState<string>('')
  const [messages, setMessages] = useState<string[]>([])

  const refreshMessages = async () => {
    const msgs = await getMessages()
    setMessages(msgs)
  }

  useEffect(() => {
    refreshMessages()
  }, [])

  const handleSubmit = async (formData: FormData) => {
    const res = await submitMessage(formData)
    setResult(JSON.stringify(res, null, 2))
    refreshMessages()
  }

  const handleDelete = async () => {
    const res = await deleteAllMessages()
    setResult(JSON.stringify(res, null, 2))
    refreshMessages()
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">CSRF Vulnerability Test App</h1>
      
      <section className="mb-8 p-4 border rounded">
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
          >
            Submit Message
          </button>
        </form>
      </section>

      <section className="mb-8 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-4">Delete All Messages (Destructive Action)</h2>
        <button 
          onClick={handleDelete}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Delete All Messages
        </button>
      </section>

      <section className="mb-8 p-4 border rounded bg-gray-100">
        <h2 className="text-xl font-semibold mb-4 text-black">Last Result:</h2>
        <pre className="bg-white p-2 rounded text-sm overflow-auto text-black">
          {result || 'No action executed yet'}
        </pre>
      </section>

      <section className="p-4 border rounded">
        <h2 className="text-xl font-semibold mb-4">Message Log:</h2>
        <ul className="list-disc pl-5">
          {messages.map((msg, i) => (
            <li key={i} className="text-sm">{msg}</li>
          ))}
          {messages.length === 0 && <li className="text-gray-500">No messages yet</li>}
        </ul>
      </section>

      <section className="mt-8 p-4 border rounded bg-yellow-50">
        <h2 className="text-xl font-semibold mb-4 text-black">Vulnerability Test Instructions:</h2>
        <pre className="text-sm text-black whitespace-pre-wrap">
{`To test CSRF with Origin: null, open this HTML from file://

<form method="POST" action="http://localhost:3000/" 
      enctype="multipart/form-data">
  <input type="hidden" name="message" value="CSRF Attack!" />
  <button>Submit</button>
</form>

The server should log a warning about missing origin but still execute.`}
        </pre>
      </section>
    </div>
  )
}
