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

# Load environment variables from .env file (must be before other imports)
from dotenv import load_dotenv
load_dotenv()

import pulumi
from pulumi_azure_native import authorization

from config import get_environment_settings


def main() -> None:
    """Deploy Azure infrastructure."""

    # Get environment from stack name
    stack_name = pulumi.get_stack()
    environment = stack_name.split("/")[-1]

    # Load environment-specific settings
    settings = get_environment_settings(environment)

    # Get Azure configuration
    azure_config = pulumi.Config("azure-native")
    client_config = authorization.get_client_config()

    pulumi.log.info(f"Deploying to environment: {environment}")
    pulumi.log.info(f"Location: {settings.location}")

    # =========================================================================
    # TODO: Implement infrastructure in this order (see docs/ARCHITECTURE.md)
    # =========================================================================
    #
    # 1. Core (Resource Groups)
    # 2. Networking (VNet, Subnets, NSGs, Private Endpoints)
    # 3. Security (Key Vault, Managed Identities)
    # 4. Observability (Log Analytics, App Insights)
    # 5. Database (Azure SQL)
    # 6. Messaging (Service Bus)
    # 7. Functions (Azure Functions - workers)
    # 8. Microservices (Container Apps)
    # 9. Gateway (API Management)
    # 10. Frontend (Static Web Apps, CDN)
    #
    # =========================================================================

    # Export environment info
    pulumi.export("environment", environment)
    pulumi.export("location", settings.location)


# Run the main function
main()
