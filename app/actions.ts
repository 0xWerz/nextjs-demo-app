'use server'

import { cookies } from 'next/headers'

// Simulating a database
let messages: string[] = []

export async function submitMessage(formData: FormData) {
  const message = formData.get('message') as string
  const session = (await cookies()).get('session')
  
  // If user is logged in, tag message with their "User ID"
  const userTag = session ? `[User: ${session.value}]` : '[Anon]'
  
  if (message) {
    console.log(`[SERVER ACTION] Executed with message: ${message}`)
    messages.push(`${userTag} ${message}`)
    return { success: true, message: `Received: ${message}` }
  }
  return { success: false }
}

export async function deleteAllMessages() {
  messages = []
  return { success: true }
}

export async function getMessages() {
  return messages
}

// === AUTHENTICATION ACTIONS ===

export async function login() {
  // Set a "Secret" session cookie
  (await cookies()).set('session', 'admin_user_' + Math.random().toString(36).substring(7), {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
  })
  return { success: true }
}

export async function logout() {
  (await cookies()).delete('session')
  return { success: true }
}

export async function getSecretData() {
  const session = (await cookies()).get('session')
  if (!session) {
    throw new Error('Unauthorized: You must be logged in to see secret data!')
  }
  return { 
    secret: "The Nuclear Launch Codes are: 1234-5678", 
    user: session.value 
  }
}
