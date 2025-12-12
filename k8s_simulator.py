#!/usr/bin/env python3
"""
Kubernetes Service Simulator
Simulates different K8s services on localhost to demonstrate status code oracle.
Run this, then test with Next.js image optimizer.
"""
import http.server
import socketserver
import threading

class ServiceHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, status_code, service_name, *args, **kwargs):
        self.status_code = status_code
        self.service_name = service_name
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        print(f"[{self.service_name}] Request: {self.path} -> Returning {self.status_code}")
        self.send_response(self.status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(f'{{"service": "{self.service_name}", "secret": "token123"}}'.encode())
    
    def log_message(self, format, *args):
        pass

def run_server(port, status_code, service_name):
    handler = lambda *args, **kwargs: ServiceHandler(status_code, service_name, *args, **kwargs)
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()

# Using high ports that won't conflict
SERVICES = [
    (9001, 200, "Kubelet API (open)"),
    (9002, 401, "Kubelet HTTPS (auth required)"),
    (9003, 403, "kube-apiserver (forbidden)"),
    (9004, 404, "etcd (not found)"),
    (9005, 500, "Internal API (error)"),
]

if __name__ == "__main__":
    print("=" * 60)
    print(" Kubernetes Service Simulator")
    print(" Demonstrates status code oracle via SSRF")
    print("=" * 60)
    print()
    
    for port, status, name in SERVICES:
        t = threading.Thread(target=run_server, args=(port, status, name), daemon=True)
        t.start()
        print(f"  127.0.0.1:{port} -> {status} ({name})")
    
    print()
    print("=" * 60)
    print("Ready! Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nDone.")
