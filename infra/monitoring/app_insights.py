"""Application Insights Component."""

from typing import Optional
import pulumi
from pulumi_azure_native import applicationinsights

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class AppInsightsComponent(pulumi.ComponentResource):
    """
    A standardized Application Insights component.

    Provides:
    - Application performance monitoring
    - Distributed tracing
    - Exception tracking
    - Custom metrics and events
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        workspace_id: pulumi.Input[str],
        application_type: str = "web",
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Application Insights component.

        Args:
            name: Logical name for the App Insights instance
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            workspace_id: Log Analytics workspace resource ID
            application_type: Application type (web, other)
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:monitoring:AppInsights", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        appi_name = generate_resource_name(
            resource_type="appi",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="monitoring")
        if extra_tags:
            tags.update(extra_tags)

        self.app_insights = applicationinsights.Component(
            appi_name,
            resource_group_name=resource_group_name,
            location=self.location,
            kind=application_type,
            application_type=applicationinsights.ApplicationType.WEB
            if application_type == "web"
            else applicationinsights.ApplicationType.OTHER,
            workspace_resource_id=workspace_id,
            disable_ip_masking=False,  # Mask IPs for privacy
            disable_local_auth=True,  # Require AAD auth
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "name": self.app_insights.name,
            "id": self.app_insights.id,
            "instrumentation_key": self.app_insights.instrumentation_key,
            "connection_string": self.app_insights.connection_string,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the App Insights name."""
        return self.app_insights.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the App Insights resource ID."""
        return self.app_insights.id

    @property
    def instrumentation_key(self) -> pulumi.Output[str]:
        """Get the instrumentation key (prefer connection string)."""
        return self.app_insights.instrumentation_key

    @property
    def connection_string(self) -> pulumi.Output[str]:
        """Get the connection string for SDK configuration."""
        return self.app_insights.connection_string
