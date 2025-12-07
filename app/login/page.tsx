'use client'

import { login, logout } from '../actions'
import { useState } from 'react'

export default function LoginPage() {
  const [status, setStatus] = useState('Logged Out')

  const handleLogin = async () => {
    await login()
    setStatus('Logged In! You can now verify the session leak.')
  }

  const handleLogout = async () => {
    await logout()
    setStatus('Logged Out')
  }

  return (
    <div className="p-10 max-w-md mx-auto space-y-6">
      <h1 className="text-3xl font-bold">🔐 Authentication Demo</h1>
      <p className="text-xl">Status: <span className="font-mono font-bold text-blue-600">{status}</span></p>
      
      <div className="flex gap-4">
        <button 
          onClick={handleLogin}
          className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 font-bold"
        >
          Login (Set Cookie)
        </button>
        
        <button 
          onClick={handleLogout}
          className="px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 font-bold"
        >
          Logout
        </button>
      </div>

      <div className="p-4 bg-gray-100 rounded text-sm text-gray-700">
        <p><strong>Instructions:</strong></p>
        <ol className="list-decimal pl-5 space-y-2 mt-2">
          <li>Click <strong>Login</strong>.</li>
          <li>This sets a secure, HTTP-only `session` cookie.</li>
          <li>Now go to the <strong>/other</strong> page (or run the PoC script).</li>
          <li>The vulnerability will leak this exact cookie.</li>
        </ol>
      </div>
    </div>
  )
}
