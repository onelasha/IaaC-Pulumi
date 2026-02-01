"""
Azure Infrastructure Modules Package.

This package contains reusable Pulumi components for Azure resources.
Each sub-module represents a logical grouping of related Azure services.

Architecture:
- core: Resource groups, naming conventions, tags
- networking: VNet, subnets, NSGs, private endpoints
- security: Key Vault, managed identities, RBAC
- frontend: Static Web Apps, CDN, DNS
- gateway: API Management, policies
- microservices: Container Apps
- messaging: Service Bus (queues, topics)
- functions: Azure Functions (workers)
- etl: ETL storage, Data Factory
- database: Azure SQL (T-SQL)
- observability: Log Analytics, App Insights, alerts
"""

# TODO: Import infrastructure stacks as they are implemented
# from .core import CoreStack
# from .networking import NetworkingStack
# from .security import SecurityStack

__all__: list[str] = []
