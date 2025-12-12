#!/usr/bin/env python3
"""
Internal API Simulation
=======================
Simulates an internal API and logs incoming connections to prove SSRF.
Run this on the victim server at 127.0.0.1:8081.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from datetime import datetime

class InternalAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] *** SSRF DETECTED! ***")
        print(f"  Client: {self.client_address[0]}:{self.client_address[1]}")
        print(f"  Path: {self.path}")
        print(f"  Host Header: {self.headers.get('Host', 'N/A')}")
        print("-" * 50)
        sys.stdout.flush()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "internal_api_response", "secret": "admin_token_12345"}')
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

if __name__ == "__main__":
    print("=" * 50)
    print(" Internal API Simulation")
    print(" Listening on 127.0.0.1:8081")
    print(" Any connections here prove SSRF succeeded!")
    print("=" * 50)
    print("\nWaiting for connections...\n")
    HTTPServer(('127.0.0.1', 8081), InternalAPIHandler).serve_forever()
