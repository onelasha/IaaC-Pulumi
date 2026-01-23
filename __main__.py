"""
Azure Infrastructure as Code with Pulumi.

This is the main entry point for the Pulumi program.
It orchestrates the deployment of all infrastructure components.
"""

# Load environment variables from .env file (must be before other imports)
from dotenv import load_dotenv
load_dotenv()

import pulumi
from pulumi_azure_native import authorization

from config import get_environment_settings
from infra.core import CoreStack
from infra.networking import NetworkingStack
from infra.security import SecurityStack
from infra.storage import StorageStack
from infra.monitoring import MonitoringStack


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
    # Core Infrastructure (Resource Groups)
    # =========================================================================
    core = CoreStack(environment=environment)

    # =========================================================================
    # Networking Infrastructure
    # =========================================================================
    networking = NetworkingStack(
        environment=environment,
        resource_group_name=core.network_rg.name,
        address_space=settings.network.vnet_address_space,
    )

    # =========================================================================
    # Security Infrastructure (Key Vault, Managed Identities)
    # =========================================================================
    security = SecurityStack(
        environment=environment,
        resource_group_name=core.security_rg.name,
        tenant_id=client_config.tenant_id,
    )

    # =========================================================================
    # Storage Infrastructure
    # =========================================================================
    storage = StorageStack(
        environment=environment,
        resource_group_name=core.data_rg.name,
    )

    # =========================================================================
    # Monitoring Infrastructure (Log Analytics, App Insights)
    # =========================================================================
    monitoring = MonitoringStack(
        environment=environment,
        resource_group_name=core.monitoring_rg.name,
    )

    # =========================================================================
    # Export Outputs
    # =========================================================================

    # Export environment info
    pulumi.export("environment", environment)
    pulumi.export("location", settings.location)

    # Export from each stack
    core.export_outputs()
    networking.export_outputs()
    security.export_outputs()
    storage.export_outputs()
    monitoring.export_outputs()


# Run the main function
main()
