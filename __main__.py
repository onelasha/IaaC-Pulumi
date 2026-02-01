"""
Azure Infrastructure as Code with Pulumi.

This is the main entry point for the Pulumi program.
It orchestrates the deployment of all infrastructure components.

Architecture:
- Frontend: Static Web Apps (React), CDN (multi-geo)
- Gateway: API Management (public, auth: basic + API key)
- Microservices: Container Apps (private)
- Messaging: Service Bus (queues, topics)
- Functions: Azure Functions (private workers)
- ETL: Python services
- Database: Azure SQL (T-SQL)
- Observability: Log Analytics, App Insights
"""

import pulumi
from pulumi_azure_native import authorization

from config import get_environment_settings, get_secrets


def main() -> None:
    """Deploy Azure infrastructure."""

    # Load secrets from .env (Pydantic auto-loads)
    secrets = get_secrets()

    # Get environment from stack name
    stack_name = pulumi.get_stack()
    environment = stack_name.split("/")[-1]

    # Load environment-specific settings
    settings = get_environment_settings(environment)

    # Get Azure client config
    client_config = authorization.get_client_config()

    pulumi.log.info(f"Deploying to environment: {environment}")
    pulumi.log.info(f"Location: {settings.location}")
    pulumi.log.info(f"State backend: {secrets.azure_storage_account}")

    # =========================================================================
    # Infrastructure deployment (see docs/ARCHITECTURE.md)
    # Uses feature flags from settings to control what gets deployed
    # =========================================================================

    # 1. Core (Resource Groups) - always deployed
    # resource_group = create_resource_group(settings)

    # 2. Networking (VNet, Subnets, NSGs) - always deployed
    # networking = create_networking(settings, resource_group)

    # 3. Security (Key Vault, Managed Identities) - always deployed
    # security = create_security(settings, resource_group)

    # 4. Observability (Log Analytics, App Insights) - always deployed
    # observability = create_observability(settings, resource_group)

    # 5. Database (Azure SQL) - conditional
    if settings.features.enable_sql_database:
        pulumi.log.info("Deploying SQL Database...")
        # database = create_database(settings, resource_group, networking)

    # 6. Messaging (Service Bus) - conditional
    if settings.features.enable_service_bus:
        pulumi.log.info("Deploying Service Bus...")
        # messaging = create_messaging(settings, resource_group)

    # 7. Functions (Azure Functions) - conditional
    if settings.features.enable_functions:
        pulumi.log.info("Deploying Azure Functions...")
        # functions = create_functions(settings, resource_group)

    # 8. Microservices (Container Apps) - conditional
    if settings.features.enable_container_apps:
        pulumi.log.info("Deploying Container Apps...")
        # microservices = create_microservices(settings, resource_group)

    # 9. Gateway (API Management) - conditional
    if settings.features.enable_api_management:
        pulumi.log.info("Deploying API Management...")
        # gateway = create_gateway(settings, resource_group)

    # 10. Frontend (CDN) - conditional
    if settings.features.enable_cdn:
        pulumi.log.info("Deploying CDN...")
        # cdn = create_cdn(settings, resource_group)

    # =========================================================================
    # Optional/Experimental Resources (dev environment testing)
    # =========================================================================

    if settings.features.enable_data_factory:
        pulumi.log.info("Deploying Data Factory (experimental)...")
        # data_factory = create_data_factory(settings, resource_group)

    if settings.features.enable_redis_cache:
        pulumi.log.info("Deploying Redis Cache...")
        # redis = create_redis(settings, resource_group)

    if settings.features.enable_cosmos_db:
        pulumi.log.info("Deploying Cosmos DB (experimental)...")
        # cosmos = create_cosmos(settings, resource_group)

    # Export environment info
    pulumi.export("environment", environment)
    pulumi.export("location", settings.location)


# Run the main function
main()
