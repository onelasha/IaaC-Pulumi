"""Resource Group Component with standardized configuration."""

from typing import Optional
import pulumi
from pulumi_azure_native import resources

from .tags import get_default_tags
from .naming import generate_resource_name


class ResourceGroupComponent(pulumi.ComponentResource):
    """
    A standardized Resource Group component with consistent naming and tagging.

    This component ensures all resource groups follow organizational standards
    for naming conventions, tagging, and location configuration.
    """

    def __init__(
        self,
        name: str,
        environment: str,
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Resource Group component.

        Args:
            name: Logical name for the resource group (e.g., 'app', 'data')
            environment: Environment name (dev, staging, prod)
            location: Azure region. If None, uses stack config
            extra_tags: Additional tags to merge with defaults
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:core:ResourceGroup", name, None, opts)

        config = pulumi.Config()
        azure_config = pulumi.Config("azure-native")

        self.location = location or azure_config.require("location")
        self.environment = environment

        # Generate standardized name
        resource_name = generate_resource_name(
            resource_type="rg",
            name=name,
            environment=environment,
        )

        # Merge tags
        tags = get_default_tags(environment=environment, component=name)
        if extra_tags:
            tags.update(extra_tags)

        # Create the resource group
        self.resource_group = resources.ResourceGroup(
            resource_name,
            resource_group_name=resource_name,
            location=self.location,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Register outputs
        self.register_outputs({
            "name": self.resource_group.name,
            "id": self.resource_group.id,
            "location": self.resource_group.location,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the resource group name."""
        return self.resource_group.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the resource group ID."""
        return self.resource_group.id
