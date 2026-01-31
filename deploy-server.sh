#!/bin/bash
# Course Companion FTE - Server Setup Script
# Run this on your WebDock VPS

set -e

echo "🚀 Starting Course Companion FTE Server Setup..."
echo ""

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker n00bi2761

# Start Docker
echo "▶️  Starting Docker..."
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo apt install docker-compose-plugin -y

# Verify Docker
echo "✅ Docker installed:"
docker --version
docker compose version

# Install Python tools
echo "🐍 Installing Python tools..."
sudo apt install python3-pip python3-venv -y
pip3 install --upgrade pip

# Install Git
echo "📦 Installing Git..."
sudo apt install git -y

# Install Node.js
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y

echo ""
echo "=== ✅ Installation Complete ==="
echo ""
echo "📊 Versions:"
docker --version
docker compose version
python3 --version
git --version
node --version
npm --version
nginx -v
echo ""
echo "🎉 Server is ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Clone your repository"
echo "2. Configure .env file"
echo "3. Run docker-compose up"
echo ""
