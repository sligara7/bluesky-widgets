#!/usr/bin/env python3
"""Simple HTTP server that disables caching for development.

Place this file in the web app directory and run it to serve files with
Cache-Control: no-cache and no ETag/Last-Modified handling so browsers
always fetch fresh copies during development.

Usage:
    python3 no_cache_server.py --port 8000 --directory .
"""
import argparse
import http.server
import socketserver
import os
import sys


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    # Serve files but ensure caching is disabled and avoid 304 handling
    def send_response_only(self, code, message=None):
        # override to avoid adding default headers here; we'll add Cache-Control later
        super().send_response_only(code, message)

    def send_header(self, keyword, value):
        # filter out ETag/Last-Modified headers set by parent
        if keyword.lower() in ("etag", "last-modified"):
            return
        return super().send_header(keyword, value)

    def end_headers(self):
        # Add headers to prevent caching
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        # Prevent the base class from sending an ETag/Last-Modified after this
        return super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # ensure error responses also include no-cache headers
        try:
            super().send_error(code, message, explain)
        except BrokenPipeError:
            pass


def run(port, directory):
    os.chdir(directory)
    handler = NoCacheHandler
    # Python 3.8+ has ThreadingHTTPServer in http.server, fallback to socketserver.ThreadingTCPServer
    try:
        httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    except AttributeError:
        class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            daemon_threads = True
        httpd = ThreadingTCPServer(("0.0.0.0", port), handler)

    print(f"Serving (no-cache) HTTP on 0.0.0.0 port {port} (http://0.0.0.0:{port}/) ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server')
        httpd.shutdown()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=8000)
    parser.add_argument('--directory', '-d', default='.')
    args = parser.parse_args(argv)
    run(args.port, args.directory)


if __name__ == '__main__':
    main()
