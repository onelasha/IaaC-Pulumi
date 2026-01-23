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
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        # Remove quotes from value
        value="${value%\"}"
        value="${value#\"}"
        # Export the variable
        export "$key=$value"
    done < <(grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -v '^[[:space:]]*$')
fi

# Check required variables
if [ -z "$AZURE_STORAGE_ACCOUNT" ]; then
    echo "Error: AZURE_STORAGE_ACCOUNT is not set in .env"
    exit 1
fi

if [ -z "$PULUMI_CONFIG_PASSPHRASE" ]; then
    echo "Warning: PULUMI_CONFIG_PASSPHRASE is empty - you will be prompted"
fi

# Run pulumi with all arguments passed to this script
exec pulumi "$@"
