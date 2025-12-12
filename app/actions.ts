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

// === VULNERABLE ACTION FOR POC ===
// This action demonstrates bound argument injection vulnerability
// The first parameter 'isAdmin' is supposed to be bound at server-side
// but through RSC protocol manipulation, attackers can inject arbitrary values

export async function adminAction(isAdmin: boolean, data: FormData) {
  console.log(`[ADMIN ACTION] Called with isAdmin=${isAdmin}`)
  
  const message = data.get('message') as string
  
  if (isAdmin !== true) {
    console.log('[SECURITY] Access denied - not admin')
    return { 
      success: false, 
      error: 'Access denied: Admin privileges required',
      isAdmin: isAdmin 
    }
  }
  
  // Admin-only operation
  console.log('[SECURITY] Admin access granted!')
  return { 
    success: true, 
    secret: 'ADMIN SECRET: Nuclear launch codes are 1234-5678',
    message: `Admin processed: ${message}`,
    isAdmin: isAdmin
  }
}

// Helper: Create a bound admin action (server-side binding)
export async function createAdminAction() {
  // This is how it SHOULD work - server binds isAdmin=true only for real admins
  const session = (await cookies()).get('session')
  const isAdmin = session?.value?.startsWith('admin_') ?? false
  
  // Return bound action reference
  return adminAction.bind(null, isAdmin)
}

// ============================================================
// REALISTIC ATTACK SCENARIO 1: BANK TRANSFER EXPLOITATION
// ============================================================
// 
// VULNERABILITY: The 'senderAccountId' is supposed to be bound server-side
// based on the authenticated user's session. However, an attacker can inject
// ANY account ID via RSC protocol manipulation, allowing them to:
// - Transfer money FROM any victim's account TO their own account
// - This is essentially unauthorized wire fraud
//
// ATTACK SCENARIO:
// 1. Victim logs in and sees their bank account balance
// 2. Attacker intercepts/crafts a transfer request
// 3. Attacker injects victim's accountId as senderAccountId
// 4. Money transfers from victim to attacker!

interface BankAccount {
  id: string
  name: string
  balance: number
}

// Simulated bank database
const bankAccounts: Record<string, BankAccount> = {
  'VICTIM-ACC-001': { id: 'VICTIM-ACC-001', name: 'Alice Victim', balance: 50000 },
  'VICTIM-ACC-002': { id: 'VICTIM-ACC-002', name: 'Bob Victim', balance: 75000 },
  'ATTACKER-ACC-999': { id: 'ATTACKER-ACC-999', name: 'Evil Hacker', balance: 100 },
}

export async function transferFunds(
  senderAccountId: string,  // VULNERABLE: Should be server-bound!
  formData: FormData
) {
  const recipientId = formData.get('recipientId') as string
  const amount = parseFloat(formData.get('amount') as string) || 0
  
  console.log(`[BANK] Transfer request: ${senderAccountId} -> ${recipientId} ($${amount})`)
  
  const sender = bankAccounts[senderAccountId]
  const recipient = bankAccounts[recipientId]
  
  if (!sender) {
    return { success: false, error: `Sender account ${senderAccountId} not found` }
  }
  if (!recipient) {
    return { success: false, error: `Recipient account ${recipientId} not found` }
  }
  if (sender.balance < amount) {
    return { success: false, error: 'Insufficient funds' }
  }
  if (amount <= 0) {
    return { success: false, error: 'Invalid amount' }
  }
  
  // Execute transfer
  sender.balance -= amount
  recipient.balance += amount
  
  console.log(`[BANK] TRANSFER COMPLETE: $${amount} from ${sender.name} to ${recipient.name}`)
  
  return {
    success: true,
    message: `Transferred $${amount} from ${sender.name} to ${recipient.name}`,
    newSenderBalance: sender.balance,
    newRecipientBalance: recipient.balance,
    transactionId: `TXN-${Date.now()}`
  }
}

export async function getAccountBalance(accountId: string) {
  const account = bankAccounts[accountId]
  if (!account) return null
  return { ...account }
}

export async function getAllAccounts() {
  return Object.values(bankAccounts)
}

// ============================================================
// REALISTIC ATTACK SCENARIO 2: E-COMMERCE PRICE MANIPULATION
// ============================================================
//
// VULNERABILITY: The 'priceInCents' is supposed to be bound server-side
// based on the product catalog. However, an attacker can inject ANY price!
//
// ATTACK SCENARIO:
// 1. Victim browses e-commerce, sees product for $999
// 2. Attacker intercepts checkout request
// 3. Attacker injects priceInCents=1 (one cent!)
// 4. Attacker buys $999 product for $0.01

interface Order {
  id: string
  product: string
  originalPrice: number
  chargedPrice: number
  timestamp: Date
}

const orders: Order[] = []

export async function checkout(
  priceInCents: number,  // VULNERABLE: Should be server-bound from catalog!
  formData: FormData
) {
  const productName = formData.get('productName') as string || 'Unknown Product'
  const catalogPrice = 99900  // Real price: $999.00
  
  console.log(`[SHOP] Checkout: ${productName} at $${(priceInCents / 100).toFixed(2)}`)
  console.log(`[SHOP] Catalog price was: $${(catalogPrice / 100).toFixed(2)}`)
  
  if (priceInCents < catalogPrice) {
    console.log(`[SHOP] ⚠️ PRICE MANIPULATION DETECTED! Charged $${(priceInCents / 100).toFixed(2)} instead of $${(catalogPrice / 100).toFixed(2)}`)
  }
  
  const order: Order = {
    id: `ORD-${Date.now()}`,
    product: productName,
    originalPrice: catalogPrice,
    chargedPrice: priceInCents,
    timestamp: new Date()
  }
  
  orders.push(order)
  
  return {
    success: true,
    orderId: order.id,
    product: productName,
    chargedAmount: `$${(priceInCents / 100).toFixed(2)}`,
    catalogPrice: `$${(catalogPrice / 100).toFixed(2)}`,
    savings: priceInCents < catalogPrice 
      ? `You saved $${((catalogPrice - priceInCents) / 100).toFixed(2)} through EXPLOITATION!`
      : undefined
  }
}

export async function getOrders() {
  return orders
}
