#!/bin/bash
# =============================================================
# VPS Ubuntu Server Setup Script
# Target: 10.132.49.100
# Purpose: Docker-based dev/CD server with GitHub Actions
# =============================================================

set -e

echo "========================================="
echo "  VPS Server Setup - Phase 1: Base Setup"
echo "========================================="

# --- Update & Essentials ---
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  curl wget git unzip htop net-tools \
  ca-certificates gnupg lsb-release \
  ufw fail2ban

# --- Firewall (UFW) ---
echo ">> Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
echo ">> Firewall enabled."

# --- Fail2Ban (brute-force protection) ---
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# --- Install Docker ---
echo ">> Installing Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker $USER

echo ">> Docker installed: $(docker --version)"
echo ">> Docker Compose: $(docker compose version)"

# --- Create directory structure ---
echo ">> Creating project directories..."
sudo mkdir -p /opt/apps/{frontend,api,nginx,runner}
sudo mkdir -p /opt/apps/nginx/{conf.d,certs}
sudo chown -R $USER:$USER /opt/apps

echo ""
echo "========================================="
echo "  Phase 1 Complete!"
echo "  Log out and back in for docker group."
echo "========================================="
