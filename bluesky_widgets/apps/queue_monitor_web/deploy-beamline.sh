#!/bin/bash
# Deployment script for BlueSky Queue Monitor Web on beamline workstation
# Run this script on the target beamline workstation after transferring the tarball

set -e

echo "BlueSky Queue Monitor Web - Beamline Deployment"
echo "================================================"

# Configuration
APP_NAME="queue_monitor_web"
INSTALL_DIR="/opt/${APP_NAME}"
NGINX_CONF="/etc/nginx/sites-available/${APP_NAME}"
QUEUE_SERVER_URL="${QUEUE_SERVER_URL:-https://vm_with_queueserver.bnl.gov:443/}"

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

echo "Installing to: $INSTALL_DIR"
echo "Queue server URL: $QUEUE_SERVER_URL"
echo ""

# Create installation directory
echo "Creating installation directory..."
$SUDO mkdir -p "$INSTALL_DIR"

# Extract application
echo "Extracting application..."
$SUDO tar -xzf "${APP_NAME}.tar.gz" -C "$INSTALL_DIR" --strip-components=1

# Update nginx configuration with correct paths and queue server URL
echo "Configuring nginx..."
$SUDO tee "$NGINX_CONF" > /dev/null << EOF
# BlueSky Queue Monitor Web - Beamline Configuration
server {
    listen 8080;
    server_name localhost;

    # Serve static files
    location / {
        root $INSTALL_DIR;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API calls to queue server
    location /api/ {
        proxy_pass $QUEUE_SERVER_URL;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Handle CORS
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization, X-Requested-With' always;

        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

# Enable nginx site
echo "Enabling nginx site..."
$SUDO ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

# Test nginx configuration
echo "Testing nginx configuration..."
if $SUDO nginx -t; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration test failed"
    exit 1
fi

# Reload nginx
echo "Reloading nginx..."
$SUDO systemctl reload nginx

# Set permissions
echo "Setting permissions..."
$SUDO chown -R www-data:www-data "$INSTALL_DIR"
$SUDO chmod -R 755 "$INSTALL_DIR"

echo ""
echo "✓ Deployment completed successfully!"
echo ""
echo "Access the application at: http://localhost:8080"
echo ""
echo "To change the queue server URL, modify QUEUE_SERVER_URL environment variable"
echo "and re-run this script, or edit $NGINX_CONF directly."
echo ""
echo "To start/stop nginx:"
echo "  sudo systemctl start nginx"
echo "  sudo systemctl stop nginx"
echo "  sudo systemctl restart nginx"