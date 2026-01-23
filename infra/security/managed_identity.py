"""Managed Identity Component for workload identity."""

from typing import Optional
import pulumi
from pulumi_azure_native import managedidentity

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class ManagedIdentityComponent(pulumi.ComponentResource):
    """
    A standardized User-Assigned Managed Identity component.

    Use managed identities to:
    - Eliminate secrets in code
    - Enable Azure AD authentication
    - Follow least-privilege access patterns
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Managed Identity component.

        Args:
            name: Logical name for the identity (e.g., 'webapp', 'function')
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:security:ManagedIdentity", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        identity_name = generate_resource_name(
            resource_type="id",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="security")
        if extra_tags:
            tags.update(extra_tags)

        self.identity = managedidentity.UserAssignedIdentity(
            identity_name,
            resource_name_=identity_name,
            resource_group_name=resource_group_name,
            location=self.location,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "name": self.identity.name,
            "id": self.identity.id,
            "principal_id": self.identity.principal_id,
            "client_id": self.identity.client_id,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the identity name."""
        return self.identity.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the identity resource ID."""
        return self.identity.id

    @property
    def principal_id(self) -> pulumi.Output[str]:
        """Get the identity's principal (object) ID for RBAC."""
        return self.identity.principal_id

    @property
    def client_id(self) -> pulumi.Output[str]:
        """Get the identity's client (application) ID."""
        return self.identity.client_id
