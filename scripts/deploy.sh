#!/usr/bin/env bash
#
# deploy.sh - Deploy infrastructure to Azure
#
# Usage:
#   ./scripts/deploy.sh <environment> [options]
#
# Arguments:
#   environment   Target environment (dev, staging, prod)
#
# Options:
#   --preview     Run preview only, don't apply changes
#   --yes         Skip confirmation prompts
#   --policy      Run with policy checks
#
# Examples:
#   ./scripts/deploy.sh dev --preview
#   ./scripts/deploy.sh prod --yes --policy
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default options
PREVIEW_ONLY=false
AUTO_APPROVE=false
USE_POLICY=false

# Parse arguments
ENVIRONMENT="${1:-}"
shift || true

while [[ $# -gt 0 ]]; do
    case $1 in
        --preview)
            PREVIEW_ONLY=true
            shift
            ;;
        --yes)
            AUTO_APPROVE=true
            shift
            ;;
        --policy)
            USE_POLICY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ -z "$ENVIRONMENT" ]]; then
    echo -e "${RED}Error: Environment is required${NC}"
    echo "Usage: $0 <environment> [options]"
    exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'${NC}"
    echo "Valid environments: dev, staging, prod"
    exit 1
fi

echo -e "${GREEN}Deploying to environment: $ENVIRONMENT${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Select the stack
echo "Selecting stack: $ENVIRONMENT"
pulumi stack select "$ENVIRONMENT" 2>/dev/null || pulumi stack init "$ENVIRONMENT"

# Build command
CMD="pulumi"

if [[ "$PREVIEW_ONLY" == true ]]; then
    CMD="$CMD preview"
else
    CMD="$CMD up"
    if [[ "$AUTO_APPROVE" == true ]]; then
        CMD="$CMD --yes"
    fi
fi

# Add policy pack if requested
if [[ "$USE_POLICY" == true ]]; then
    CMD="$CMD --policy-pack ./policies"
fi

# Run deployment
echo -e "${YELLOW}Running: $CMD${NC}"
eval "$CMD"

echo -e "${GREEN}Deployment complete!${NC}"
