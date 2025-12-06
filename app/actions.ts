'use server'

// Simulated sensitive action - in real app this would modify data
let messageLog: string[] = []

export async function submitMessage(formData: FormData) {
  const message = formData.get('message') as string
  const timestamp = new Date().toISOString()
  
  // Log the action execution - this is the "vulnerable" action
  messageLog.push(`[${timestamp}] Message: ${message}`)
  console.log(`[SERVER ACTION] Executed with message: ${message}`)
  
  return { 
    success: true, 
    message: `Action executed! Message received: ${message}`,
    timestamp 
  }
}

export async function deleteAllMessages() {
  // Sensitive action - deletes all data
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
