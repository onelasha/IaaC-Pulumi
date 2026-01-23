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

# Core components (implemented)
from .core import CoreStack

# Networking components (implemented)
from .networking import NetworkingStack

# Security components (implemented)
from .security import SecurityStack

# TODO: Implement remaining stacks
# from .frontend import FrontendStack
# from .gateway import GatewayStack
# from .microservices import MicroservicesStack
# from .messaging import MessagingStack
# from .functions import FunctionsStack
# from .etl import EtlStack
# from .database import DatabaseStack
# from .observability import ObservabilityStack

__all__ = [
    "CoreStack",
    "NetworkingStack",
    "SecurityStack",
    # "FrontendStack",
    # "GatewayStack",
    # "MicroservicesStack",
    # "MessagingStack",
    # "FunctionsStack",
    # "EtlStack",
    # "DatabaseStack",
    # "ObservabilityStack",
]
