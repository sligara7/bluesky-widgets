#!/usr/bin/env python3
"""
Simple HTTP server for BlueSky Queue Monitor Web with CORS support.
Run this from the queue_monitor_web directory to serve the web app.
"""

import http.server
import socketserver
import os
from urllib.parse import urlparse, parse_qs

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Serve BlueSky Queue Monitor Web with CORS')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
    parser.add_argument('--bind', default='0.0.0.0', help='Address to bind to')

    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer((args.bind, args.port), CORSHTTPRequestHandler) as httpd:
        print(f"Serving BlueSky Queue Monitor Web at http://{args.bind}:{args.port}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")