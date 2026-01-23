"""Monitoring Stack - Observability infrastructure setup."""

from typing import Optional
import pulumi

from .log_analytics import LogAnalyticsComponent
from .app_insights import AppInsightsComponent


class MonitoringStack:
    """
    Monitoring infrastructure stack.

    Creates centralized logging and application monitoring
    following observability best practices.
    """

    def __init__(
        self,
        environment: str,
        resource_group_name: pulumi.Input[str],
        config: Optional[pulumi.Config] = None,
    ):
        """
        Initialize the monitoring stack.

        Args:
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group for monitoring resources
            config: Optional Pulumi config
        """
        self.environment = environment
        self.config = config or pulumi.Config()
        self.resource_group_name = resource_group_name

        self._create_monitoring_resources()

    def _create_monitoring_resources(self) -> None:
        """Create monitoring resources."""

        # Retention days based on environment
        retention_days = {
            "dev": 30,
            "staging": 60,
            "prod": 90,
        }.get(self.environment, 30)

        # Central Log Analytics Workspace
        self.log_analytics = LogAnalyticsComponent(
            name="central",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            retention_days=retention_days,
        )

        # Application Insights for app monitoring
        self.app_insights = AppInsightsComponent(
            name="app",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            workspace_id=self.log_analytics.id,
        )

    def export_outputs(self) -> dict[str, pulumi.Output]:
        """Export stack outputs."""
        outputs = {
            "log_analytics_workspace_name": self.log_analytics.name,
            "log_analytics_workspace_id": self.log_analytics.workspace_id,
            "app_insights_name": self.app_insights.name,
            "app_insights_connection_string": self.app_insights.connection_string,
        }

        for name, value in outputs.items():
            pulumi.export(name, value)

        return outputs
