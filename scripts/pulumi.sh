#!/bin/bash
# Wrapper script to run Pulumi with .env variables loaded
#
# Usage:
#   ./scripts/pulumi.sh preview
#   ./scripts/pulumi.sh up
#   ./scripts/pulumi.sh destroy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env file if it exists
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Check required variables
if [ -z "$AZURE_STORAGE_ACCOUNT" ]; then
    echo "Error: AZURE_STORAGE_ACCOUNT is not set in .env"
    exit 1
fi

if [ -z "${PULUMI_CONFIG_PASSPHRASE+x}" ]; then
    echo "Warning: PULUMI_CONFIG_PASSPHRASE is not set - you will be prompted"
fi

# Run pulumi with all arguments passed to this script
exec pulumi "$@"
