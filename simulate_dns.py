#!/usr/bin/env python3
"""
Simulates dns_4query.py output for demonstration.
"""
import time

print("=" * 50)
print(" 4-Query DNS Rebinding Server")
print("=" * 50)
print("Next.js image optimizer makes 4 DNS queries:")
print("  Q1-Q2: lookup() validation → PUBLIC IP (passes check)")
print("  Q3-Q4: fetch() request     → PRIVATE IP (SSRF!)")
print("=" * 50)
print()

time.sleep(2)

# Simulate incoming queries
queries = [
    ("127.0.0.1", 1, "8.8.8.8"),
    ("127.0.0.1", 2, "8.8.8.8"),
    ("127.0.0.1", 3, "127.0.0.1"),
    ("127.0.0.1", 4, "127.0.0.1"),
]

for client, q_num, ip in queries:
    print(f"[{client}] Q{q_num} -> {ip}")
    time.sleep(0.3)

print()
print("SSRF successful - Next.js connected to 127.0.0.1!")
