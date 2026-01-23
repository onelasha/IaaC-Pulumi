# Azure Infrastructure as Code with Pulumi

A production-ready Pulumi project for provisioning Azure cloud resources using Python and uv. This project follows DevSecOps best practices with modular architecture, security policies, and comprehensive testing.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Bootstrap Infrastructure](#bootstrap-infrastructure-one-time-setup)
- [Quick Start](#quick-start)
- [State Backend Configuration](#state-backend-configuration)
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

## Bootstrap Infrastructure (One-time Setup)

These resources store Pulumi state and must be created **manually** before using this project. They are intentionally not managed by Pulumi to avoid circular dependencies.

```bash
# Create resource group for infrastructure
az group create --name rg-infra --location westus2

# Create storage account for Pulumi state
az storage account create \
  --name pulumistateonelasha \
  --resource-group rg-infra \
  --location westus2 \
  --sku Standard_LRS \
  --kind StorageV2

# Create container for state files
az storage container create \
  --name pulumi-state \
  --account-name pulumistateonelasha
```

> **Why not manage this with Pulumi?** Pulumi needs its state backend to exist before it can run. If Pulumi managed its own state storage and accidentally destroyed it, all state would be lost. Keeping bootstrap infrastructure separate is a safety best practice.

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

# List available subscriptions and find your subscription ID
az account list --output table

# Set your subscription (use the SubscriptionId from the list above)
az account set --subscription "<subscription-id>"

# Verify authentication and confirm correct subscription is selected
az account show --output table
```

Example output from `az account list`:
```
Name                  SubscriptionId                        State    IsDefault
--------------------  ------------------------------------  -------  ----------
Developer G           xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  Enabled  True
Production            yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  Enabled  False
```

> **Tip**: If you only have one subscription, it will be set as default automatically after `az login`.

### 3. Initialize Pulumi Stack

```bash
# Set Azure Storage backend (recommended for teams)
export AZURE_STORAGE_ACCOUNT=pulumistateonelasha
pulumi login azblob://pulumi-state

# Alternative backends:
# pulumi login --local  # For local state (testing only)
# pulumi login          # For Pulumi Cloud

# Select existing stack OR create new one
pulumi stack select dev 2>/dev/null || pulumi stack init dev
```

> **Note**: Use `stack select` for existing stacks, `stack init` for new ones. Neither command provisions resources—they only manage stack metadata. See [State Backend Configuration](#state-backend-configuration) for detailed setup instructions.

### 4. Configure the Stack

```bash
# Set Azure location
pulumi config set azure-native:location westus2

# Optional: Set owner and cost center for tagging
pulumi config set owner "Platform Team"
pulumi config set costCenter "IT-001"
```

### 5. Deploy

> **Best Practice**: Always preview before applying. Never deploy without reviewing what will change.

```bash
# ALWAYS preview first - see exactly what will be created/modified/deleted
pulumi preview

# Review the output carefully, then deploy
pulumi up

# Or use the deploy script (--preview is recommended first)
./scripts/deploy.sh dev --preview  # Review changes
./scripts/deploy.sh dev            # Apply after review
```

## State Backend Configuration

Pulumi state can be stored in different backends. This project uses **Azure Blob Storage** for secure, centralized state management.

### Azure Blob Storage Backend (Recommended for Teams)

We use the storage account `pulumistateonelasha` for storing Pulumi state files.

#### Initial Setup

**Step 1: Set the storage account environment variable**

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc) for persistence
export AZURE_STORAGE_ACCOUNT=pulumistateonelasha
```

**Step 2: Create a container for state (one-time setup)**

```bash
# Create the container if it doesn't exist
az storage container create \
  --name pulumi-state \
  --account-name pulumistateonelasha
```

**Step 3: Login to Pulumi with Azure Blob backend**

```bash
pulumi login azblob://pulumi-state
```

**Step 4: Verify connection**

```bash
pulumi whoami -v
```

Expected output:
```
User: <your-user>
Backend URL: azblob://pulumi-state
```

### Authentication Methods

| Method | Environment Variable | Use Case |
|--------|---------------------|----------|
| Azure CLI (Recommended) | None - uses `az login` session | Local development |
| Storage Account Key | `AZURE_STORAGE_KEY=<key>` | CI/CD pipelines |
| SAS Token | `AZURE_STORAGE_SAS_TOKEN=<token>` | Limited access scenarios |
| Service Principal | `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_TENANT_ID` | Automated deployments |

#### Using Azure CLI Authentication (Local Development)

```bash
# Login to Azure first
az login

# List subscriptions to find your subscription ID
az account list --output table

# Set subscription (if you have multiple subscriptions)
az account set --subscription "<subscription-id-from-list>"

# Login to Pulumi backend
export AZURE_STORAGE_ACCOUNT=pulumistateonelasha
pulumi login azblob://pulumi-state
```

#### Using Storage Account Key (CI/CD)

```bash
# Get the storage account key
export AZURE_STORAGE_KEY=$(az storage account keys list \
  --account-name pulumistateonelasha \
  --query '[0].value' -o tsv)

export AZURE_STORAGE_ACCOUNT=pulumistateonelasha
pulumi login azblob://pulumi-state
```

#### Using Service Principal (Automated Pipelines)

```bash
export ARM_CLIENT_ID="<service-principal-app-id>"
export ARM_CLIENT_SECRET="<service-principal-password>"
export ARM_TENANT_ID="<azure-tenant-id>"
export ARM_SUBSCRIPTION_ID="<azure-subscription-id>"
export AZURE_STORAGE_ACCOUNT=pulumistateonelasha

pulumi login azblob://pulumi-state
```

### Backend Comparison

| Backend | Command | Best For |
|---------|---------|----------|
| Azure Blob Storage | `pulumi login azblob://pulumi-state` | Team collaboration, enterprise |
| Pulumi Cloud | `pulumi login` | SaaS convenience, built-in UI |
| Local Filesystem | `pulumi login --local` | Individual testing only |
| AWS S3 | `pulumi login s3://bucket-name` | AWS-centric organizations |

### State Management Best Practices

1. **Never commit state files** - They may contain secrets
2. **Enable versioning** on the storage container for state recovery
3. **Use encryption** - Azure Storage encrypts at rest by default
4. **Restrict access** - Use RBAC to limit who can access state
5. **Backup regularly** - Enable soft delete on the container

#### Enable Versioning and Soft Delete (Recommended)

```bash
# Enable blob versioning
az storage account blob-service-properties update \
  --account-name pulumistateonelasha \
  --enable-versioning true

# Enable soft delete (7-day retention)
az storage blob service-properties delete-policy update \
  --account-name pulumistateonelasha \
  --enable true \
  --days-retained 7
```

### Migrating Between Backends

To migrate state from local to Azure Blob:

```bash
# Export current stack state
pulumi stack export --file stack-backup.json

# Login to new backend
export AZURE_STORAGE_ACCOUNT=pulumistateonelasha
pulumi login azblob://pulumi-state

# Initialize stack in new backend
pulumi stack init dev

# Import state
pulumi stack import --file stack-backup.json
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `unauthorized` error | Run `az login` and ensure correct subscription |
| `container not found` | Create container: `az storage container create --name pulumi-state --account-name pulumistateonelasha` |
| `AZURE_STORAGE_ACCOUNT not set` | Export the environment variable |
| State locked | Another operation in progress; wait or manually remove `.pulumi/locks` |

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

# ALWAYS preview first - verify before you apply
pulumi preview

# Deploy only after reviewing the preview
pulumi up

# Destroy (use with caution - preview first!)
pulumi preview --diff   # See what will be destroyed
pulumi destroy
```

### CI/CD Integration

Example GitHub Actions workflow with Azure Blob Storage backend:

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AZURE_STORAGE_ACCOUNT: pulumistateonelasha
  ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
  ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
  ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
  ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: |
            {
              "clientId": "${{ secrets.ARM_CLIENT_ID }}",
              "clientSecret": "${{ secrets.ARM_CLIENT_SECRET }}",
              "subscriptionId": "${{ secrets.ARM_SUBSCRIPTION_ID }}",
              "tenantId": "${{ secrets.ARM_TENANT_ID }}"
            }

      - name: Pulumi Preview
        uses: pulumi/actions@v5
        with:
          command: preview
          stack-name: dev
          cloud-url: azblob://pulumi-state

  deploy:
    needs: preview
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync

      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: |
            {
              "clientId": "${{ secrets.ARM_CLIENT_ID }}",
              "clientSecret": "${{ secrets.ARM_CLIENT_SECRET }}",
              "subscriptionId": "${{ secrets.ARM_SUBSCRIPTION_ID }}",
              "tenantId": "${{ secrets.ARM_TENANT_ID }}"
            }

      - name: Pulumi Deploy
        uses: pulumi/actions@v5
        with:
          command: up
          stack-name: dev
          cloud-url: azblob://pulumi-state
```

#### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `ARM_CLIENT_ID` | Service Principal Application ID |
| `ARM_CLIENT_SECRET` | Service Principal Password |
| `ARM_TENANT_ID` | Azure AD Tenant ID |
| `ARM_SUBSCRIPTION_ID` | Azure Subscription ID |

> **Note**: The Service Principal needs `Storage Blob Data Contributor` role on the `pulumistateonelasha` storage account.

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
