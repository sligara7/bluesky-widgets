#!/bin/bash
# Deployment script for BlueSky Queue Monitor Web
# Usage: ./deploy.sh <beamline-name> <queue-server-url>

set -e

BEAMLINE_NAME=$1
QUEUE_SERVER_URL=$2

if [ -z "$BEAMLINE_NAME" ] || [ -z "$QUEUE_SERVER_URL" ]; then
    echo "Usage: $0 <beamline-name> <queue-server-url>"
    echo "Example: $0 beamline1 https://queue-bl1.bnl.gov:443"
    exit 1
fi

echo "Deploying BlueSky Queue Monitor for $BEAMLINE_NAME"
echo "Queue Server: $QUEUE_SERVER_URL"

# Create deployment directory
DEPLOY_DIR="/var/www/queue-monitor-$BEAMLINE_NAME"
sudo mkdir -p "$DEPLOY_DIR"

# Copy web files
sudo cp -r * "$DEPLOY_DIR/"

# Create nginx configuration
NGINX_CONF="/etc/nginx/sites-available/queue-monitor-$BEAMLINE_NAME"

sudo tee "$NGINX_CONF" > /dev/null <<EOF
# Nginx configuration for $BEAMLINE_NAME queue monitor
server {
    listen 80;
    server_name queue-monitor-$BEAMLINE_NAME.nsls2.bnl.gov;

    # Serve static files
    location / {
        root $DEPLOY_DIR;
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
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Enable site
sudo ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/"

# Test configuration
sudo nginx -t

echo "Deployment complete!"
echo "Site enabled at: queue-monitor-$BEAMLINE_NAME.nsls2.bnl.gov"
echo "Queue server: $QUEUE_SERVER_URL"
echo ""
echo "To activate:"
echo "  sudo systemctl reload nginx"
echo ""
echo "To test:"
echo "  curl http://queue-monitor-$BEAMLINE_NAME.nsls2.bnl.gov"