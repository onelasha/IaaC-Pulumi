# Azure Infrastructure as Code with Pulumi

A production-ready Pulumi project for provisioning Azure cloud resources using Python and uv. This project follows DevSecOps best practices with modular architecture, security policies, and comprehensive testing.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Modules](#modules)
- [Configuration](#configuration)
- [Security Policies](#security-policies)
- [Testing](#testing)
- [Deployment](#deployment)
- [Naming Conventions](#naming-conventions)
- [Tagging Strategy](#tagging-strategy)
- [Contributing](#contributing)

## Project Structure

```
.
├── __main__.py              # Main Pulumi program entry point
├── Pulumi.yaml              # Pulumi project configuration
├── Pulumi.dev.yaml          # Dev environment stack config
├── pyproject.toml           # Python project configuration (uv)
├── uv.lock                  # Dependency lock file
│
├── infra/                   # Infrastructure modules
│   ├── __init__.py
│   ├── core/                # Core resources (resource groups, naming, tags)
│   │   ├── __init__.py
│   │   ├── naming.py        # Naming convention utilities
│   │   ├── resource_group.py
│   │   ├── stack.py
│   │   └── tags.py          # Tagging utilities
│   ├── networking/          # Network resources (VNet, NSG, etc.)
│   │   ├── __init__.py
│   │   ├── nsg.py
│   │   ├── stack.py
│   │   └── vnet.py
│   ├── security/            # Security resources (Key Vault, identities)
│   │   ├── __init__.py
│   │   ├── keyvault.py
│   │   ├── managed_identity.py
│   │   └── stack.py
│   ├── storage/             # Storage resources
│   │   ├── __init__.py
│   │   ├── stack.py
│   │   └── storage_account.py
│   ├── monitoring/          # Monitoring resources (Log Analytics, App Insights)
│   │   ├── __init__.py
│   │   ├── app_insights.py
│   │   ├── log_analytics.py
│   │   └── stack.py
│   ├── compute/             # Compute resources (VMs, AKS) - extensible
│   │   └── __init__.py
│   └── database/            # Database resources - extensible
│       └── __init__.py
│
├── config/                  # Environment configurations
│   ├── __init__.py
│   └── settings.py          # Environment-specific settings
│
├── policies/                # Pulumi CrossGuard policies
│   ├── __init__.py
│   ├── PulumiPolicy.yaml
│   └── security_policies.py # Security compliance policies
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   │   ├── __init__.py
│   │   ├── test_naming.py
│   │   └── test_tags.py
│   └── integration/         # Integration tests
│       └── __init__.py
│
├── scripts/                 # Deployment and utility scripts
│   ├── deploy.sh            # Deployment script
│   └── validate.sh          # Validation script
│
└── docs/                    # Additional documentation
```

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| [Python](https://python.org) | >= 3.12 | Runtime |
| [uv](https://github.com/astral-sh/uv) | Latest | Python package manager |
| [Pulumi CLI](https://www.pulumi.com/docs/install/) | >= 3.0 | Infrastructure deployment |
| [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) | Latest | Azure authentication |

### Azure Requirements

- An Azure subscription with sufficient permissions
- Service Principal or Azure CLI authentication configured
- Contributor role (minimum) on target subscription

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Pulumi

# Install dependencies with uv
uv sync

# Install dev dependencies (optional)
uv sync --extra dev
```

### 2. Azure Authentication

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "<subscription-id>"

# Verify authentication
az account show
```

### 3. Initialize Pulumi Stack

```bash
# Login to Pulumi (local backend or Pulumi Cloud)
pulumi login --local  # For local state
# OR
pulumi login          # For Pulumi Cloud

# Create a new stack for your environment
pulumi stack init dev
```

### 4. Configure the Stack

```bash
# Set Azure location
pulumi config set azure-native:location westus2

# Optional: Set owner and cost center for tagging
pulumi config set owner "Platform Team"
pulumi config set costCenter "IT-001"
```

### 5. Deploy

```bash
# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# Or use the deploy script
./scripts/deploy.sh dev --preview
./scripts/deploy.sh dev
```

## Architecture

This project implements a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      __main__.py                            │
│                   (Orchestration Layer)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   CoreStack   │   │NetworkingStack│   │ SecurityStack │
│               │   │               │   │               │
│ - ResourceGrps│   │ - VNet        │   │ - Key Vault   │
│ - Tags        │   │ - Subnets     │   │ - Identities  │
│ - Naming      │   │ - NSGs        │   │ - RBAC        │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ StorageStack  │   │MonitoringStack│   │  ComputeStack │
│               │   │               │   │  (extensible) │
│ - Storage Acct│   │ - Log Analytic│   │ - VMs         │
│ - Containers  │   │ - App Insights│   │ - AKS         │
└───────────────┘   └───────────────┘   └───────────────┘
```

### Design Principles

1. **Component-Based**: Each resource type is wrapped in a Pulumi ComponentResource
2. **Environment-Aware**: Configuration changes per environment (dev/staging/prod)
3. **Security-First**: Private endpoints, RBAC, encryption by default
4. **Observable**: Centralized logging and monitoring
5. **Testable**: Unit tests for naming and tagging logic

## Modules

### Core (`infra/core/`)

Foundation module providing:
- **Resource Groups**: Standardized resource group creation
- **Naming**: Consistent naming conventions per Azure limits
- **Tagging**: Default tags for cost allocation and governance

### Networking (`infra/networking/`)

Network infrastructure:
- **VNet**: Virtual networks with subnet segmentation
- **NSG**: Network security groups with tier-based rules
- **Service Endpoints**: Secure access to Azure services

### Security (`infra/security/`)

Security resources:
- **Key Vault**: Secrets management with RBAC
- **Managed Identity**: Workload identity for passwordless auth

### Storage (`infra/storage/`)

Storage resources:
- **Storage Account**: Secure blob storage with soft delete
- **Containers**: Pre-configured blob containers

### Monitoring (`infra/monitoring/`)

Observability:
- **Log Analytics**: Centralized logging workspace
- **App Insights**: Application performance monitoring

## Configuration

### Environment Settings

Environment-specific settings are defined in `config/settings.py`:

| Environment | VNet CIDR | Purge Protection | Log Retention |
|-------------|-----------|------------------|---------------|
| dev | 10.0.0.0/16 | Disabled | 30 days |
| staging | 10.1.0.0/16 | Disabled | 60 days |
| prod | 10.2.0.0/16 | Enabled | 365 days |

### Stack Configuration

Stack-specific values in `Pulumi.<env>.yaml`:

```yaml
config:
  azure-native:location: westus2
  azureinfra:owner: Platform Team
  azureinfra:costCenter: IT-001
```

## Security Policies

This project includes Pulumi CrossGuard policies for compliance:

| Policy | Description | Enforcement |
|--------|-------------|-------------|
| `storage-https-only` | Storage accounts must use HTTPS | Mandatory |
| `storage-tls-version` | Minimum TLS 1.2 required | Mandatory |
| `storage-no-public-access` | No public blob access | Mandatory |
| `keyvault-purge-protection` | Purge protection in prod | Mandatory |
| `required-tags` | Required tags present | Mandatory |
| `nsg-no-open-to-internet` | No open inbound rules | Mandatory |

### Running with Policies

```bash
# Preview with policy checks
pulumi preview --policy-pack ./policies

# Deploy with policy checks
pulumi up --policy-pack ./policies
```

## Testing

### Run Unit Tests

```bash
# Install test dependencies
uv sync --extra dev

# Run all unit tests
pytest tests/unit -v

# Run with coverage
pytest tests/unit --cov=infra --cov-report=html
```

### Validation Script

```bash
# Run all validation checks
./scripts/validate.sh

# Quick validation (skip slow checks)
./scripts/validate.sh --quick

# Auto-fix linting issues
./scripts/validate.sh --fix
```

## Deployment

### Using Scripts

```bash
# Preview deployment
./scripts/deploy.sh dev --preview

# Deploy to dev
./scripts/deploy.sh dev

# Deploy to prod with policy checks
./scripts/deploy.sh prod --policy

# Auto-approve deployment
./scripts/deploy.sh staging --yes
```

### Manual Deployment

```bash
# Select stack
pulumi stack select dev

# Preview
pulumi preview

# Deploy
pulumi up

# Destroy (use with caution!)
pulumi destroy
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - uses: pulumi/actions@v5
        with:
          command: preview
          stack-name: dev
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
```

## Naming Conventions

Resources follow Azure naming best practices:

| Resource | Format | Example |
|----------|--------|---------|
| Resource Group | `rg-{name}-{env}` | `rg-app-dev` |
| Storage Account | `st{name}{env}` | `stappdev` |
| Key Vault | `kv-{name}-{env}` | `kv-main-prod` |
| VNet | `vnet-{name}-{env}` | `vnet-main-dev` |
| Subnet | `snet-{name}-{env}` | `snet-app-dev` |
| NSG | `nsg-{name}-{env}` | `nsg-web-dev` |

See `infra/core/naming.py` for implementation details.

## Tagging Strategy

All resources are tagged with:

| Tag | Description | Example |
|-----|-------------|---------|
| `Environment` | Deployment environment | `dev`, `prod` |
| `ManagedBy` | Automation tool | `Pulumi` |
| `Project` | Pulumi project name | `AzureInfra` |
| `Stack` | Pulumi stack name | `dev` |
| `CreatedDate` | Resource creation date | `2025-01-22` |
| `Component` | Logical component | `networking` |
| `Owner` | Team/individual owner | `Platform Team` |
| `CostCenter` | Cost allocation | `IT-001` |

## Contributing

### Development Workflow

1. Create a feature branch
2. Make changes
3. Run validation: `./scripts/validate.sh`
4. Test with preview: `pulumi preview`
5. Create pull request
6. Review and merge

### Adding New Resources

1. Create component in appropriate module (e.g., `infra/compute/aks.py`)
2. Export from module `__init__.py`
3. Add to stack class if needed
4. Add unit tests
5. Update documentation

### Code Style

- Use type hints for all functions
- Follow PEP 8 (enforced by ruff)
- Document public functions with docstrings
- Keep components focused and single-purpose

## Getting Help

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Azure Native Provider](https://www.pulumi.com/registry/packages/azure-native/)
- [Pulumi Community Slack](https://slack.pulumi.com/)
- [Azure Documentation](https://docs.microsoft.com/azure/)

## License

MIT License - see LICENSE file for details.
