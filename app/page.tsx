'use client'
// Force git update


import { submitMessage, deleteAllMessages, getMessages, adminAction, transferFunds, checkout, getAllAccounts } from './actions'
import { useState, useEffect } from 'react'
import Link from 'next/link'

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
      
      {/* INTERCEPTION TEST LINK */}
      <section className="mb-8 p-4 border rounded bg-blue-50">
        <h2 className="text-xl font-semibold mb-4 text-black">Interception Route Test</h2>
        <Link 
          href="/photos" 
          className="px-6 py-3 bg-green-500 text-white rounded hover:bg-green-600 inline-block"
        >
          📷 View Photos (Click to test interception)
        </Link>
      </section>

      {/* SSRF STATUS CODE ORACLE TEST */}
      <section className="mb-8 p-4 border rounded bg-red-50">
        <h2 className="text-xl font-semibold mb-4 text-black">🔥 SSRF Status Code Oracle Test</h2>
        <p className="text-sm text-black mb-4">These images trigger requests to simulated K8s services. Check browser network tab for status codes!</p>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <p className="text-black text-sm">Port 9001 (200 OK)</p>
            <img src="/_next/image?url=http://127.0.0.1:9001/pods&w=64&q=75" alt="9001" width={64} height={64} />
          </div>
          <div className="text-center">
            <p className="text-black text-sm">Port 9002 (401 Auth)</p>
            <img src="/_next/image?url=http://127.0.0.1:9002/api&w=64&q=75" alt="9002" width={64} height={64} />
          </div>
          <div className="text-center">
            <p className="text-black text-sm">Port 9003 (403 Forbidden)</p>
            <img src="/_next/image?url=http://127.0.0.1:9003/secrets&w=64&q=75" alt="9003" width={64} height={64} />
          </div>
          <div className="text-center">
            <p className="text-black text-sm">Port 9004 (404 Not Found)</p>
            <img src="/_next/image?url=http://127.0.0.1:9004/etcd&w=64&q=75" alt="9004" width={64} height={64} />
          </div>
          <div className="text-center col-span-2">
            <p className="text-black text-sm">Port 9005 (500 Error)</p>
            <img src="/_next/image?url=http://127.0.0.1:9005/internal&w=64&q=75" alt="9005" width={64} height={64} />
          </div>
        </div>
      </section>
      
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

      {/* BANK TRANSFER - REALISTIC ATTACK SCENARIO */}
      <section className="mb-8 p-4 border rounded bg-green-50">
        <h2 className="text-xl font-semibold mb-4 text-black">🏦 Bank Transfer (Vulnerable)</h2>
        <p className="text-sm text-black mb-2">Scenario: senderAccountId should be server-bound from session.</p>
        <p className="text-sm text-red-600 mb-4">ATTACK: Attacker injects victim&apos;s account ID to steal funds!</p>
        <form action={async (formData) => {
          // VULNERABLE: senderAccountId comes from client!
          // Attacker can change this to any victim's account
          const res = await transferFunds('ATTACKER-ACC-999', formData)
          setResult(JSON.stringify(res, null, 2))
        }} className="space-y-4">
          <input type="hidden" name="recipientId" value="ATTACKER-ACC-999" />
          <input 
            type="number" 
            name="amount" 
            placeholder="Amount to transfer"
            defaultValue="10000"
            className="w-full p-2 border rounded text-black"
          />
          <button 
            type="submit"
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Transfer from MY account (Normal)
          </button>
        </form>
      </section>

      {/* E-COMMERCE CHECKOUT - PRICE MANIPULATION */}
      <section className="mb-8 p-4 border rounded bg-orange-50">
        <h2 className="text-xl font-semibold mb-4 text-black">🛒 E-Commerce Checkout (Vulnerable)</h2>
        <p className="text-sm text-black mb-2">Scenario: priceInCents should be server-bound from product catalog.</p>
        <p className="text-sm text-red-600 mb-4">ATTACK: Attacker injects priceInCents=1 to buy $999 item for $0.01!</p>
        <form action={async (formData) => {
          // VULNERABLE: priceInCents comes from client!
          // Should be: 99900 ($999.00) from catalog
          // Attacker injects: 1 ($0.01)
          const res = await checkout(99900, formData)  // Normal price
          setResult(JSON.stringify(res, null, 2))
        }} className="space-y-4">
          <input type="hidden" name="productName" value="MacBook Pro M4" />
          <p className="text-black">Product: MacBook Pro M4 - <strong>$999.00</strong></p>
          <button 
            type="submit"
            className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600"
          >
            Buy Now (Normal Price)
          </button>
        </form>
      </section>

      {/* ADMIN ACTION TEST - For RSC Bound Injection PoC */}
      <section className="mb-8 p-4 border rounded bg-purple-50">
        <h2 className="text-xl font-semibold mb-4 text-black">🔐 Admin Action Test (RSC PoC)</h2>
        <p className="text-sm text-black mb-4">This action expects isAdmin=true as first bound argument.</p>
        <form action={async (formData) => {
          const res = await adminAction(false, formData)  // Normally isAdmin=false
          setResult(JSON.stringify(res, null, 2))
        }} className="space-y-4">
          <input 
            type="text" 
            name="message" 
            placeholder="Admin message..."
            className="w-full p-2 border rounded text-black"
          />
          <button 
            type="submit"
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            Test Admin Action (isAdmin=false)
          </button>
        </form>
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
