"""Serve and install helpers for the BlueSky Queue Monitor Web static app.

Provides utilities to locate the installed static files and either run a
dev HTTP server or copy the files to a target directory (for nginx to serve).

Usage:
  python -m bluesky_widgets.apps.queue_monitor_web.serve --port 8000
  queue-monitor-web --port 8000
  queue-monitor-web --copy-to /opt/queue_monitor_web
"""
from __future__ import annotations

import argparse
import http.server
import os
import shutil
import socketserver
import sys
from importlib import resources
from pathlib import Path


def get_static_path() -> Path:
    """Return a filesystem Path to the installed `queue_monitor_web` static files.

    Uses importlib.resources.files to work with both editable installs and
    installed wheels.
    """
    # Try to locate the installed package on the filesystem via module __file__.
    try:
        import bluesky_widgets.apps.queue_monitor_web as pkg

        pkg_path = Path(pkg.__file__).resolve().parent
        if pkg_path.exists():
            return pkg_path
    except Exception:
        pass

    # Fallback: use importlib.resources to copy files into a persistent temp dir.
    package_root = resources.files("bluesky_widgets.apps.queue_monitor_web")
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="queue_monitor_web_"))
    for item in package_root.iterdir():
        target = tmp / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    return tmp


def run_dev_server(port: int = 8000, bind: str = "127.0.0.1") -> None:
    static_path = get_static_path()
    os.chdir(static_path)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            super().end_headers()

        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()

    with socketserver.TCPServer((bind, port), Handler) as httpd:
        print(f"Serving BlueSky Queue Monitor Web at http://{bind}:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")


def install_to_dir(target: str) -> None:
    """Copy installed static files to target directory.

    If target requires elevated permissions, run this script with sudo/appropriate rights.
    """
    static_path = get_static_path()
    target_path = Path(target)
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.copytree(static_path, target_path)
    print(f"Copied web assets to {target_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="BlueSky Queue Monitor Web helper")
    parser.add_argument("--port", type=int, default=8000, help="Port for dev server")
    parser.add_argument("--bind", default="127.0.0.1", help="Bind address for dev server")
    parser.add_argument("--copy-to", help="Copy the installed web assets to this directory")
    args = parser.parse_args(argv)

    if args.copy_to:
        install_to_dir(args.copy_to)
        return

    run_dev_server(port=args.port, bind=args.bind)


if __name__ == "__main__":
    main()
