"""Storage Stack - Storage infrastructure setup."""

from typing import Optional
import pulumi

from .storage_account import StorageAccountComponent


class StorageStack:
    """
    Storage infrastructure stack.

    Creates storage accounts with proper security configuration
    and container structure.
    """

    def __init__(
        self,
        environment: str,
        resource_group_name: pulumi.Input[str],
        config: Optional[pulumi.Config] = None,
    ):
        """
        Initialize the storage stack.

        Args:
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group for storage resources
            config: Optional Pulumi config
        """
        self.environment = environment
        self.config = config or pulumi.Config()
        self.resource_group_name = resource_group_name

        self._create_storage_resources()

    def _create_storage_resources(self) -> None:
        """Create storage resources."""

        # Application data storage
        self.app_storage = StorageAccountComponent(
            name="app",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            sku="Standard_LRS",
            containers=["data", "uploads", "exports"],
        )

        # Logs and diagnostics storage
        self.logs_storage = StorageAccountComponent(
            name="logs",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            sku="Standard_LRS",
            access_tier="Cool",
            containers=["diagnostics", "audit", "flow-logs"],
        )

    def export_outputs(self) -> dict[str, pulumi.Output]:
        """Export stack outputs."""
        outputs = {
            "app_storage_name": self.app_storage.name,
            "app_storage_blob_endpoint": self.app_storage.primary_blob_endpoint,
            "logs_storage_name": self.logs_storage.name,
        }

        for name, value in outputs.items():
            pulumi.export(name, value)

        return outputs
