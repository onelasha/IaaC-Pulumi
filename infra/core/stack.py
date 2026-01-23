"""Core Stack - Foundation infrastructure setup."""

from typing import Optional
import pulumi
from pulumi_azure_native import resources

from .resource_group import ResourceGroupComponent
from .tags import get_default_tags


class CoreStack:
    """
    Core infrastructure stack containing foundational resources.

    This stack creates the base resource groups and shared resources
    that other stacks depend on.
    """

    def __init__(
        self,
        environment: str,
        config: Optional[pulumi.Config] = None,
    ):
        """
        Initialize the core stack.

        Args:
            environment: Environment name (dev, staging, prod)
            config: Optional Pulumi config, defaults to current stack config
        """
        self.environment = environment
        self.config = config or pulumi.Config()

        # Create core resource groups
        self._create_resource_groups()

    def _create_resource_groups(self) -> None:
        """Create standard resource groups for the environment."""

        # Main application resource group
        self.app_rg = ResourceGroupComponent(
            name="app",
            environment=self.environment,
            extra_tags={"Purpose": "Application Resources"},
        )

        # Networking resource group
        self.network_rg = ResourceGroupComponent(
            name="network",
            environment=self.environment,
            extra_tags={"Purpose": "Networking Resources"},
        )

        # Security resource group (Key Vault, Managed Identities)
        self.security_rg = ResourceGroupComponent(
            name="security",
            environment=self.environment,
            extra_tags={"Purpose": "Security Resources"},
        )

        # Monitoring resource group
        self.monitoring_rg = ResourceGroupComponent(
            name="monitoring",
            environment=self.environment,
            extra_tags={"Purpose": "Monitoring and Observability"},
        )

        # Data resource group (databases, storage)
        self.data_rg = ResourceGroupComponent(
            name="data",
            environment=self.environment,
            extra_tags={"Purpose": "Data and Storage Resources"},
        )

    def export_outputs(self) -> dict[str, pulumi.Output]:
        """
        Export stack outputs.

        Returns:
            Dictionary of output names to values
        """
        outputs = {
            "app_resource_group_name": self.app_rg.name,
            "network_resource_group_name": self.network_rg.name,
            "security_resource_group_name": self.security_rg.name,
            "monitoring_resource_group_name": self.monitoring_rg.name,
            "data_resource_group_name": self.data_rg.name,
        }

        for name, value in outputs.items():
            pulumi.export(name, value)

        return outputs
