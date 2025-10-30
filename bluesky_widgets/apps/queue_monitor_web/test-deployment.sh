#!/bin/bash
# Test script for BlueSky Queue Monitor Web deployment on beamline workstation
# Run this after deployment to verify everything is working

echo "Testing BlueSky Queue Monitor Web Deployment"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test nginx configuration
echo -n "Testing nginx configuration... "
if sudo nginx -t 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Run 'sudo nginx -t' to see the error details"
    exit 1
fi

# Test nginx service
echo -n "Testing nginx service... "
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Nginx service is not running. Try: sudo systemctl start nginx"
    exit 1
fi

# Test web application accessibility
echo -n "Testing web application... "
if curl -s -f http://localhost:8080/index.html > /dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Cannot access http://localhost:8080/index.html"
    exit 1
fi

# Test API proxy (will fail if queue server is not reachable, but that's expected)
echo -n "Testing API proxy configuration... "
if curl -s -I http://localhost:8080/api/status 2>/dev/null | grep -q "200\|404\|500"; then
    echo -e "${GREEN}✓ PASS${NC} (proxy responding)"
elif curl -s -I http://localhost:8080/api/status 2>/dev/null | grep -q "502\|503\|504"; then
    echo -e "${YELLOW}⚠ WARN${NC} (queue server not reachable - expected on test systems)"
else
    echo -e "${RED}✗ FAIL${NC} (proxy not configured correctly)"
fi

echo ""
echo -e "${GREEN}Basic deployment tests completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:8080 in a browser"
echo "2. Configure the queue server URL in the web app settings"
echo "3. Test connection to your actual queue server"
echo ""
echo "For remote access from your development machine:"
echo "  ssh -L 8080:localhost:8080 beamline-ws.nsls2.bnl.gov"
echo "  Then open http://localhost:8080 in your local browser"