"""Log Analytics Workspace Component."""

from typing import Optional
import pulumi
from pulumi_azure_native import operationalinsights

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class LogAnalyticsComponent(pulumi.ComponentResource):
    """
    A standardized Log Analytics Workspace component.

    Central logging for:
    - Azure resource diagnostics
    - Container insights
    - Security Center
    - Custom application logs
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        retention_days: int = 30,
        daily_quota_gb: Optional[float] = None,
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Log Analytics Workspace component.

        Args:
            name: Logical name for the workspace
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            retention_days: Data retention in days (30-730)
            daily_quota_gb: Daily ingestion cap in GB
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:monitoring:LogAnalytics", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        workspace_name = generate_resource_name(
            resource_type="law",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="monitoring")
        if extra_tags:
            tags.update(extra_tags)

        # Set retention based on environment
        if environment == "prod":
            retention_days = max(retention_days, 90)

        self.workspace = operationalinsights.Workspace(
            workspace_name,
            workspace_name=workspace_name,
            resource_group_name=resource_group_name,
            location=self.location,
            sku=operationalinsights.WorkspaceSkuArgs(
                name=operationalinsights.WorkspaceSkuNameEnum.PER_GB2018,
            ),
            retention_in_days=retention_days,
            workspace_capping=operationalinsights.WorkspaceCappingArgs(
                daily_quota_gb=daily_quota_gb or -1,  # -1 means no limit
            ) if daily_quota_gb else None,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "name": self.workspace.name,
            "id": self.workspace.id,
            "workspace_id": self.workspace.customer_id,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the workspace name."""
        return self.workspace.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the workspace resource ID."""
        return self.workspace.id

    @property
    def workspace_id(self) -> pulumi.Output[str]:
        """Get the workspace GUID (customer ID)."""
        return self.workspace.customer_id
