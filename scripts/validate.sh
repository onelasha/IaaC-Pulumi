#!/usr/bin/env bash
#
# validate.sh - Validate infrastructure code
#
# Runs linting, type checking, and tests before deployment.
#
# Usage:
#   ./scripts/validate.sh [options]
#
# Options:
#   --fix     Attempt to auto-fix issues
#   --quick   Skip slow checks (type checking, full tests)
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

AUTO_FIX=false
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            AUTO_FIX=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

echo -e "${YELLOW}=== Validating Infrastructure Code ===${NC}\n"

# Step 1: Check Python syntax
echo -e "${YELLOW}[1/4] Checking Python syntax...${NC}"
if python -m py_compile __main__.py; then
    echo -e "${GREEN}  ✓ Syntax OK${NC}"
else
    echo -e "${RED}  ✗ Syntax errors found${NC}"
    exit 1
fi

# Step 2: Run linter (ruff)
echo -e "\n${YELLOW}[2/4] Running linter...${NC}"
if command -v ruff &> /dev/null; then
    if [[ "$AUTO_FIX" == true ]]; then
        ruff check --fix . || true
        ruff format .
    else
        if ruff check .; then
            echo -e "${GREEN}  ✓ No linting issues${NC}"
        else
            echo -e "${RED}  ✗ Linting issues found (run with --fix to auto-fix)${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}  ⚠ ruff not installed, skipping${NC}"
fi

# Step 3: Type checking (mypy)
if [[ "$QUICK_MODE" == false ]]; then
    echo -e "\n${YELLOW}[3/4] Running type checker...${NC}"
    if command -v mypy &> /dev/null; then
        if mypy --ignore-missing-imports infra/; then
            echo -e "${GREEN}  ✓ Type checking passed${NC}"
        else
            echo -e "${YELLOW}  ⚠ Type checking found issues${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠ mypy not installed, skipping${NC}"
    fi
else
    echo -e "\n${YELLOW}[3/4] Skipping type checker (quick mode)${NC}"
fi

# Step 4: Run tests
if [[ "$QUICK_MODE" == false ]]; then
    echo -e "\n${YELLOW}[4/4] Running tests...${NC}"
    if command -v pytest &> /dev/null; then
        if pytest tests/unit -v --tb=short; then
            echo -e "${GREEN}  ✓ All tests passed${NC}"
        else
            echo -e "${RED}  ✗ Some tests failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}  ⚠ pytest not installed, skipping${NC}"
    fi
else
    echo -e "\n${YELLOW}[4/4] Skipping tests (quick mode)${NC}"
fi

echo -e "\n${GREEN}=== Validation Complete ===${NC}"
