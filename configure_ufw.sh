#!/bin/bash
# UFW Firewall Configuration for DFIR Vendor Analysis Platform

echo "=== UFW Firewall Configuration ==="
echo "Configuring firewall to allow port 5000 from any IP..."

# Enable UFW if not already enabled
sudo ufw --force enable

# Allow port 5000 TCP (HTTP)
echo "Allowing port 5000/tcp from any IP..."
sudo ufw allow 5000/tcp

# Allow port 5000 UDP (optional, for future enhancements)
echo "Allowing port 5000/udp from any IP..."
sudo ufw allow 5000/udp

# Show status
echo ""
echo "=== Current UFW Status ==="
sudo ufw status numbered

# Show specifically port 5000 rules
echo ""
echo "=== Port 5000 Rules ==="
sudo ufw show added | grep 5000

echo ""
echo "✅ Firewall configuration complete!"
echo "Port 5000 is now accessible from any IP address."
