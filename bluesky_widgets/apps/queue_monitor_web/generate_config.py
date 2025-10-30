#!/usr/bin/env python3
"""
Configuration generator for BlueSky Queue Monitor Web
Generates nginx configuration for different beamlines
"""

import argparse
import os

def generate_nginx_config(beamline_name, queue_server_url, output_file=None):
    """Generate nginx configuration for a specific beamline"""

    config = f"""# Nginx configuration for {beamline_name} queue monitor
# Generated automatically - do not edit manually

server {{
    listen 80;
    server_name queue-monitor-{beamline_name}.nsls2.bnl.gov;

    # Serve static files
    location / {{
        root /var/www/queue-monitor-{beamline_name};
        index index.html;
        try_files $uri $uri/ /index.html;
    }}

    # Proxy API calls to queue server
    location /api/ {{
        proxy_pass {queue_server_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Handle CORS
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

        if ($request_method = 'OPTIONS') {{
            return 204;
        }}
    }}

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Logs
    access_log /var/log/nginx/queue-monitor-{beamline_name}.access.log;
    error_log /var/log/nginx/queue-monitor-{beamline_name}.error.log;
}}
"""

    if output_file:
        with open(output_file, 'w') as f:
            f.write(config)
        print(f"Configuration written to {output_file}")
    else:
        print(config)

def main():
    parser = argparse.ArgumentParser(description='Generate nginx config for queue monitor')
    parser.add_argument('beamline', help='Beamline name (e.g., bl1, bl2)')
    parser.add_argument('queue_url', help='Queue server URL (e.g., https://queue-bl1.bnl.gov:443)')
    parser.add_argument('-o', '--output', help='Output file path')

    args = parser.parse_args()

    generate_nginx_config(args.beamline, args.queue_url, args.output)

if __name__ == '__main__':
    main()