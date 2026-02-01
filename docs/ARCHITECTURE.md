# Architecture Plan

## Overview

A serverless, event-driven Azure architecture with public API gateway, private microservices, and multi-geo frontend delivery.

## Architecture Diagram

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                        INTERNET                              │
                                    └─────────────────────────────────────────────────────────────┘
                                                            │
                        ┌───────────────────────────────────┼───────────────────────────────────┐
                        │                                   │                                   │
                        ▼                                   ▼                                   ▼
              ┌─────────────────┐                ┌─────────────────┐                  ┌─────────────────┐
              │   Azure CDN     │                │ API Management  │                  │   Azure CDN     │
              │   (West US)     │                │    (Gateway)    │                  │   (West EU)     │
              └────────┬────────┘                └────────┬────────┘                  └────────┬────────┘
                       │                                  │                                    │
                       ▼                                  │                                    ▼
              ┌─────────────────┐                         │                           ┌─────────────────┐
              │ Static Web App  │                         │ Basic Auth + API Key      │ Static Web App  │
              │    (React)      │                         │                           │    (React)      │
              └─────────────────┘                         │                           └─────────────────┘
                                                          │
┌─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┐
│                                          PRIVATE VNET   │                                                         │
│  ┌──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────┐  │
│  │                                    APP SUBNET        │                                                      │  │
│  │                                                      ▼                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                   │  │
│  │  │  Microservice   │    │  Microservice   │    │  Microservice   │    │  Microservice   │                   │  │
│  │  │   (Users)       │    │   (Orders)      │    │   (Products)    │    │   (Payments)    │                   │  │
│  │  │ Container App   │    │ Container App   │    │ Container App   │    │ Container App   │                   │  │
│  │  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘                   │  │
│  │           │                      │                      │                      │                            │  │
│  └───────────┼──────────────────────┼──────────────────────┼──────────────────────┼────────────────────────────┘  │
│              │                      │                      │                      │                               │
│  ┌───────────┼──────────────────────┼──────────────────────┼──────────────────────┼────────────────────────────┐  │
│  │           │              INTEGRATION SUBNET             │                      │                            │  │
│  │           ▼                      ▼                      ▼                      ▼                            │  │
│  │  ┌───────────────────────────────────────────────────────────────────────────────────────┐                  │  │
│  │  │                              Azure Service Bus                                         │                  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │                  │  │
│  │  │  │ orders-queue│  │events-topic │  │ etl-queue   │  │notify-topic │  │ dlq-queue   │  │                  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │                  │  │
│  │  └───────────────────────────────────────────────────────────────────────────────────────┘                  │  │
│  │                                              │                                                              │  │
│  └──────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┘  │
│                                                 │                                                                 │
│  ┌──────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┐  │
│  │                           FUNCTIONS SUBNET   │                                                              │  │
│  │                                              ▼                                                              │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                   │  │
│  │  │ Azure Function  │    │ Azure Function  │    │ Azure Function  │    │ Azure Function  │                   │  │
│  │  │ (Queue Worker)  │    │ (Topic Worker)  │    │ (ETL Processor) │    │ (3rd Party Sync)│                   │  │
│  │  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘                   │  │
│  │           │                      │                      │                      │                            │  │
│  │           │                      │                      │              ┌───────┴───────┐                    │  │
│  │           │                      │                      │              │ Third-Party   │                    │  │
│  │           │                      │                      │              │ APIs (egress) │                    │  │
│  │           │                      │                      │              └───────────────┘                    │  │
│  └───────────┼──────────────────────┼──────────────────────┼───────────────────────────────────────────────────┘  │
│              │                      │                      │                                                      │
│  ┌───────────┼──────────────────────┼──────────────────────┼───────────────────────────────────────────────────┐  │
│  │           │                DATA SUBNET                  │                                                   │  │
│  │           ▼                      ▼                      ▼                                                   │  │
│  │  ┌───────────────────────────────────────────────────────────────┐    ┌─────────────────┐                   │  │
│  │  │                      Azure SQL Database                       │    │  Blob Storage   │                   │  │
│  │  │                          (T-SQL)                              │    │  (ETL staging)  │                   │  │
│  │  └───────────────────────────────────────────────────────────────┘    └─────────────────┘                   │  │
│  │                                                                                                             │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────────────────────────┐
                    │                         OBSERVABILITY                                │
                    │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
                    │  │  Log Analytics  │    │  App Insights   │    │ Azure Monitor   │  │
                    │  │   Workspace     │    │  (APM + Traces) │    │    Alerts       │  │
                    │  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
                    └─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend Layer (Public)

| Component      | Azure Service          | Purpose                    |
| -------------- | ---------------------- | -------------------------- |
| Static Web App | Azure Static Web Apps  | React SPA hosting          |
| CDN            | Azure CDN / Front Door | Multi-geo content delivery |
| Custom Domain  | Azure DNS              | Domain management          |

**Regions**: West US, West Europe (expandable)

### 2. API Gateway Layer (Public)

| Component      | Azure Service        | Purpose                         |
| -------------- | -------------------- | ------------------------------- |
| API Gateway    | Azure API Management | Centralized API entry point     |
| Authentication | APIM Policies        | Basic auth + API key validation |
| Rate Limiting  | APIM Policies        | Throttling and quotas           |
| Caching        | APIM Cache           | Response caching                |

**Security**:

- Basic Authentication (username/password)
- API Key (subscription key)
- IP filtering (optional)
- OAuth 2.0 (future enhancement)

### 3. Microservices Layer (Private)

| Component         | Azure Service              | Purpose                  |
| ----------------- | -------------------------- | ------------------------ |
| Microservices     | Azure Container Apps       | Business logic services  |
| Service Discovery | Container Apps Environment | Internal service routing |
| Scaling           | KEDA                       | Event-driven autoscaling |

**Services** (examples):

- `users-api` - User management
- `orders-api` - Order processing
- `products-api` - Product catalog
- `payments-api` - Payment processing

### 4. Messaging Layer (Private)

| Component      | Azure Service      | Purpose                  |
| -------------- | ------------------ | ------------------------ |
| Message Broker | Azure Service Bus  | Async messaging          |
| Queues         | Service Bus Queues | Point-to-point messaging |
| Topics         | Service Bus Topics | Pub/sub messaging        |
| Dead Letter    | DLQ                | Failed message handling  |

**Queues/Topics**:

- `orders-queue` - Order processing
- `events-topic` - Domain events
- `etl-queue` - ETL job triggers
- `notifications-topic` - Notification distribution
- `thirdparty-queue` - External API calls

### 5. Functions Layer (Private Workers)

| Component         | Azure Service   | Purpose                  |
| ----------------- | --------------- | ------------------------ |
| Queue Workers     | Azure Functions | Process queue messages   |
| Topic Subscribers | Azure Functions | React to events          |
| ETL Processors    | Azure Functions | Data transformation      |
| Third-party Sync  | Azure Functions | External API integration |

**Triggers**:

- Service Bus Queue trigger
- Service Bus Topic trigger
- Timer trigger (scheduled ETL)
- HTTP trigger (internal only)

### 6. ETL Layer (Private)

| Component         | Azure Service            | Purpose                          |
| ----------------- | ------------------------ | -------------------------------- |
| ETL Orchestration | Azure Functions (Python) | Data pipeline logic              |
| Staging Storage   | Blob Storage             | Intermediate data storage        |
| Data Factory      | Azure Data Factory       | Complex ETL workflows (optional) |

### 7. Database Layer (Private)

| Component        | Azure Service      | Purpose                    |
| ---------------- | ------------------ | -------------------------- |
| Primary Database | Azure SQL Database | Transactional data (T-SQL) |
| Connection       | Private Endpoint   | Secure database access     |
| Backup           | Azure SQL Backup   | Point-in-time recovery     |

### 8. Security Layer

| Component | Azure Service        | Purpose                        |
| --------- | -------------------- | ------------------------------ |
| Secrets   | Azure Key Vault      | API keys, connection strings   |
| Identity  | Managed Identity     | Passwordless Azure auth        |
| Network   | Private Endpoints    | No public database/service bus |
| WAF       | Azure Front Door WAF | Web application firewall       |

### 9. Observability Layer

| Component  | Azure Service           | Purpose                        |
| ---------- | ----------------------- | ------------------------------ |
| Logs       | Log Analytics Workspace | Centralized logging            |
| APM        | Application Insights    | Performance monitoring, traces |
| Metrics    | Azure Monitor           | Infrastructure metrics         |
| Alerts     | Azure Monitor Alerts    | Proactive notifications        |
| Dashboards | Azure Workbooks         | Visualization                  |

## Network Architecture

### Subnets

| Subnet      | CIDR | Purpose                             |
| ----------- | ---- | ----------------------------------- |
| gateway     | /24  | API Management (if VNet integrated) |
| app         | /24  | Container Apps                      |
| functions   | /24  | Azure Functions                     |
| integration | /24  | Service Bus Private Endpoints       |
| data        | /24  | SQL + Storage Private Endpoints     |
| management  | /24  | Bastion, Jump boxes (optional)      |

### Access Control

| From           | To               | Access                 |
| -------------- | ---------------- | ---------------------- |
| Internet       | Static Web App   | Public (CDN)           |
| Internet       | API Management   | Public (with auth)     |
| API Management | Microservices    | Private (VNet)         |
| Microservices  | Service Bus      | Private Endpoint       |
| Microservices  | SQL Database     | Private Endpoint       |
| Functions      | Service Bus      | Private Endpoint       |
| Functions      | Third-party APIs | Outbound (NAT Gateway) |

## Folder Structure

```
infra/
├── core/                    # Shared utilities
│   ├── naming.py            # Resource naming conventions
│   ├── tags.py              # Tagging strategy
│   └── resource_group.py    # Resource group component
│
├── networking/              # Network infrastructure
│   ├── vnet.py              # Virtual network
│   ├── subnets.py           # Subnet definitions
│   ├── nsg.py               # Network security groups
│   ├── private_endpoints.py # Private endpoint management
│   └── nat_gateway.py       # Outbound connectivity
│
├── frontend/                # Public web layer
│   ├── static_web_app.py    # Azure Static Web Apps
│   ├── cdn.py               # CDN / Front Door
│   └── dns.py               # Custom domains
│
├── gateway/                 # API Gateway
│   ├── apim.py              # API Management instance
│   ├── apis.py              # API definitions
│   ├── products.py          # API products & subscriptions
│   └── policies.py          # Auth, rate limiting policies
│
├── microservices/           # Container Apps
│   ├── environment.py       # Container Apps Environment
│   ├── container_app.py     # Container App component
│   └── dapr.py              # Dapr configuration (optional)
│
├── messaging/               # Event-driven messaging
│   ├── servicebus.py        # Service Bus namespace
│   ├── queues.py            # Queue definitions
│   └── topics.py            # Topic definitions
│
├── functions/               # Serverless workers
│   ├── function_app.py      # Function App component
│   ├── app_service_plan.py  # Consumption/Premium plan
│   └── storage.py           # Function storage account
│
├── etl/                     # Data processing
│   ├── storage.py           # ETL staging storage
│   └── data_factory.py      # ADF pipelines (optional)
│
├── database/                # Data layer
│   ├── sql_server.py        # Azure SQL Server
│   ├── sql_database.py      # Database instance
│   └── firewall.py          # SQL firewall rules
│
├── security/                # Security resources
│   ├── keyvault.py          # Key Vault
│   ├── managed_identity.py  # Managed identities
│   └── rbac.py              # Role assignments
│
└── observability/           # Monitoring & logging
    ├── log_analytics.py     # Log Analytics workspace
    ├── app_insights.py      # Application Insights
    └── alerts.py            # Alert rules
```

## Deployment Order

Dependencies require this deployment sequence:

```
1. Core (Resource Groups)
        │
        ▼
2. Networking (VNet, Subnets, NSGs)
        │
        ▼
3. Security (Key Vault, Managed Identities)
        │
        ├──────────────────────┬─────────────────────┐
        ▼                      ▼                     ▼
4. Observability          5. Database           6. Messaging
   (Log Analytics,           (SQL Server,          (Service Bus)
    App Insights)             SQL Database)
        │                      │                     │
        └──────────────────────┴─────────────────────┘
                               │
                               ▼
                    7. Functions (Workers)
                               │
                               ▼
                    8. Microservices (Container Apps)
                               │
                               ▼
                    9. Gateway (API Management)
                               │
                               ▼
                    10. Frontend (Static Web Apps, CDN)
```

## Environment Strategy

| Environment | Purpose               | Regions                          |
| ----------- | --------------------- | -------------------------------- |
| dev         | Development & testing | West US 2                        |
| qa          | Quality assurance     | West US 2                        |
| staging     | Pre-production        | West US 2                        |
| prod        | Production            | West US 2 (+ West Europe future) |

## Environment Management

### Configuration Layers (Pydantic)

This project uses **Pydantic** for type-safe configuration management:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION LAYERS (Pydantic)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  .env                          SECRETS (same for all environments)  │   │
│  │  ├── PULUMI_CONFIG_PASSPHRASE  Encryption passphrase                │   │
│  │  ├── AZURE_STORAGE_ACCOUNT     State backend (pulumistateonelasha)  │   │
│  │  └── ARM_*                     Service principal (CI/CD)            │   │
│  │                                                                     │   │
│  │  Loaded by: AppSecrets (pydantic-settings) → get_secrets()          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Pulumi.<stack>.yaml           STACK CONFIG (per environment)       │   │
│  │  ├── Pulumi.dev.yaml           encryptionsalt, location, owner      │   │
│  │  ├── Pulumi.qa.yaml            encryptionsalt, location, owner      │   │
│  │  ├── Pulumi.staging.yaml       encryptionsalt, location, owner      │   │
│  │  └── Pulumi.prod.yaml          encryptionsalt, location, owner      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  config/settings.py            INFRA SETTINGS (per environment)     │   │
│  │  ├── NetworkSettings           VNet CIDR, subnets, DDoS, firewall   │   │
│  │  ├── SecuritySettings          purge protection, private endpoints  │   │
│  │  ├── MonitoringSettings        retention days, quotas               │   │
│  │  └── FeatureFlags              which resources to deploy            │   │
│  │                                                                     │   │
│  │  Loaded by: EnvironmentSettings (Pydantic) → get_environment_settings()│
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Pydantic Models:**

| Class                 | Purpose                                            |
| --------------------- | -------------------------------------------------- |
| `AppSecrets`          | Loads secrets from `.env` with `SecretStr` masking |
| `NetworkSettings`     | VNet, subnets, DDoS, firewall config               |
| `SecuritySettings`    | Key Vault, private endpoints config                |
| `MonitoringSettings`  | Log retention, quotas                              |
| `FeatureFlags`        | Controls which resources deploy per environment    |
| `EnvironmentSettings` | Combines all settings for an environment           |

### Network Isolation by Environment

| Environment | VNet CIDR   | Purpose                        |
| ----------- | ----------- | ------------------------------ |
| dev         | 10.0.0.0/16 | Development - relaxed security |
| qa          | 10.3.0.0/16 | QA testing - mirrors staging   |
| staging     | 10.1.0.0/16 | Pre-prod - mirrors production  |
| prod        | 10.2.0.0/16 | Production - full security     |

### Environment-Specific Settings

| Setting              | Dev | QA  | Staging | Prod      |
| -------------------- | --- | --- | ------- | --------- |
| DDoS Protection      | ❌  | ❌  | ❌      | ✅        |
| Firewall             | ❌  | ❌  | ❌      | ✅        |
| Private Endpoints    | ❌  | ❌  | ✅      | ✅        |
| Purge Protection     | ❌  | ❌  | ❌      | ✅        |
| Soft Delete (days)   | 7   | 14  | 30      | 90        |
| Log Retention (days) | 30  | 30  | 60      | 365       |
| Daily Quota (GB)     | 1   | 2   | 5       | Unlimited |

### Feature Flags

Feature flags in `config/settings.py` control which resources are deployed per environment. This enables:

- **Dev** to have experimental resources for testing
- **QA** to be minimal and cost-effective
- **Staging/Prod** to have production-ready resources

| Feature        | Dev | QA  | Staging | Prod | Purpose             |
| -------------- | --- | --- | ------- | ---- | ------------------- |
| Container Apps | ✅  | ✅  | ✅      | ✅   | Microservices       |
| Functions      | ✅  | ✅  | ✅      | ✅   | Serverless workers  |
| Service Bus    | ✅  | ✅  | ✅      | ✅   | Messaging           |
| SQL Database   | ✅  | ✅  | ✅      | ✅   | Primary database    |
| API Management | ✅  | ❌  | ✅      | ✅   | API gateway         |
| CDN            | ❌  | ❌  | ✅      | ✅   | Content delivery    |
| Data Factory   | ✅  | ❌  | ❌      | ❌   | ETL (dev testing)   |
| Redis Cache    | ✅  | ❌  | ❌      | ✅   | Caching             |
| Cosmos DB      | ✅  | ❌  | ❌      | ❌   | NoSQL (dev testing) |

Usage in `__main__.py`:

```python
settings = get_environment_settings(environment)

# Conditional resource deployment
if settings.features.enable_sql_database:
    database = create_database(settings, resource_group)

if settings.features.enable_cosmos_db:  # Only in dev!
    cosmos = create_cosmos(settings, resource_group)
```

### Deployment Commands

```bash
# Select and deploy to specific environment
pulumi stack select dev && pulumi up
pulumi stack select qa && pulumi up
pulumi stack select staging && pulumi up
pulumi stack select prod && pulumi up

# Or use --stack flag
pulumi up --stack dev
pulumi up --stack qa
pulumi up --stack staging
pulumi up --stack prod
```

### State Management

All environments share a single Azure Storage backend:

- **Storage Account**: `pulumistateonelasha`
- **Resource Group**: `rg-infra`
- **Location**: West US 2

Each stack maintains its own state file within the storage account.

## Cost Optimization

| Component      | Dev/Staging    | Production           |
| -------------- | -------------- | -------------------- |
| API Management | Developer tier | Standard tier        |
| Container Apps | Consumption    | Consumption (scaled) |
| Functions      | Consumption    | Premium (VNet)       |
| SQL Database   | Basic          | Standard S2+         |
| Service Bus    | Basic          | Standard             |

## Next Steps

1. [x] Review and approve this architecture
2. [x] Set up folder structure
3. [x] Configure multi-environment support (dev, qa, staging, prod)
4. [x] Implement feature flags for conditional resource deployment
5. [ ] Implement core module (naming, tags, resource groups)
6. [ ] Implement networking module (VNet, subnets, NSGs)
7. [ ] Implement security module (Key Vault, managed identities)
8. [ ] Implement observability module (Log Analytics, App Insights)
9. [ ] Implement remaining modules in dependency order
10. [ ] Add security policies (CrossGuard)
11. [ ] Set up CI/CD pipelines
