#!/bin/bash
# =============================================================
# GitHub Actions Self-Hosted Runner Setup
# Run this ON the VPS after Phase 1
# =============================================================
# 
# OPTION A: Self-hosted runner (recommended - no SSH keys needed)
# OPTION B: SSH-based deploy (simpler, uses SSH from GitHub Actions)
#
# This script sets up OPTION A.
# For Option B, skip this and just add SSH keys to GitHub secrets.
# =============================================================

set -e

RUNNER_DIR="/opt/apps/runner"
cd $RUNNER_DIR

echo "========================================="
echo "  GitHub Actions Self-Hosted Runner Setup"
echo "========================================="
echo ""
echo "1. Go to your GitHub repo → Settings → Actions → Runners"
echo "2. Click 'New self-hosted runner'"
echo "3. Select Linux x64"
echo "4. Copy the token shown there"
echo ""
read -p "Paste your runner token: " RUNNER_TOKEN
read -p "Your GitHub org/user: " GITHUB_OWNER
read -p "Your repo name (or leave blank for org-level): " REPO_NAME

# Download latest runner
RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep -oP '"tag_name": "v\K[^"]+')
curl -o actions-runner-linux-x64.tar.gz -L \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

tar xzf actions-runner-linux-x64.tar.gz
rm actions-runner-linux-x64.tar.gz

# Configure
if [ -z "$REPO_NAME" ]; then
  ./config.sh --url "https://github.com/${GITHUB_OWNER}" --token "$RUNNER_TOKEN" --labels "vps,docker,production" --unattended
else
  ./config.sh --url "https://github.com/${GITHUB_OWNER}/${REPO_NAME}" --token "$RUNNER_TOKEN" --labels "vps,docker,production" --unattended
fi

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start

echo ""
echo "========================================="
echo "  Runner installed and running!"
echo "  Labels: vps, docker, production"
echo "========================================="
