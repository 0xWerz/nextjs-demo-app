'use server'

import { cookies } from 'next/headers'

// Simulating a database
let messages: string[] = []

export async function submitMessage(formData: FormData) {
  const message = formData.get('message') as string
  const session = cookies().get('session')
  
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
  const count = messageLog.length
  messageLog = []
  console.log(`[SERVER ACTION] Deleted ${count} messages`)
  
  return { 
    success: true, 
    deletedCount: count 
  }
}

export async function getMessages() {
  return messageLog
}
