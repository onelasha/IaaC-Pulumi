"""Environment-specific settings and configuration."""

from dataclasses import dataclass, field
from typing import Optional
import pulumi


@dataclass
class NetworkSettings:
    """Network configuration for an environment."""

    vnet_address_space: list[str]
    subnet_prefixes: dict[str, str]
    enable_ddos_protection: bool = False
    enable_firewall: bool = False


@dataclass
class SecuritySettings:
    """Security configuration for an environment."""

    enable_purge_protection: bool = False
    soft_delete_retention_days: int = 30
    enable_private_endpoints: bool = False
    allowed_ip_ranges: list[str] = field(default_factory=list)


@dataclass
class MonitoringSettings:
    """Monitoring configuration for an environment."""

    log_retention_days: int = 30
    enable_diagnostic_settings: bool = True
    daily_quota_gb: Optional[float] = None


@dataclass
class FeatureFlags:
    """Feature flags to control which resources are deployed per environment."""

    enable_container_apps: bool = True
    enable_functions: bool = True
    enable_service_bus: bool = True
    enable_sql_database: bool = True
    enable_api_management: bool = True
    enable_cdn: bool = False
    enable_data_factory: bool = False
    enable_redis_cache: bool = False
    enable_cosmos_db: bool = False


@dataclass
class EnvironmentSettings:
    """Complete settings for an environment."""

    name: str
    location: str
    network: NetworkSettings
    security: SecuritySettings
    monitoring: MonitoringSettings
    features: FeatureFlags = field(default_factory=FeatureFlags)
    tags: dict[str, str] = field(default_factory=dict)


# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    "dev": EnvironmentSettings(
        name="dev",
        location="westus2",
        network=NetworkSettings(
            vnet_address_space=["10.0.0.0/16"],
            subnet_prefixes={
                "gateway": "10.0.0.0/24",
                "web": "10.0.1.0/24",
                "app": "10.0.2.0/24",
                "data": "10.0.3.0/24",
                "management": "10.0.4.0/24",
            },
            enable_ddos_protection=False,
            enable_firewall=False,
        ),
        security=SecuritySettings(
            enable_purge_protection=False,
            soft_delete_retention_days=7,
            enable_private_endpoints=False,
        ),
        monitoring=MonitoringSettings(
            log_retention_days=30,
            daily_quota_gb=1.0,
        ),
        features=FeatureFlags(
            enable_container_apps=True,
            enable_functions=True,
            enable_service_bus=True,
            enable_sql_database=True,
            enable_api_management=True,
            enable_cdn=False,
            enable_data_factory=True,   # Dev: testing ETL pipelines
            enable_redis_cache=True,    # Dev: testing caching
            enable_cosmos_db=True,      # Dev: testing NoSQL
        ),
    ),
    "qa": EnvironmentSettings(
        name="qa",
        location="westus2",
        network=NetworkSettings(
            vnet_address_space=["10.3.0.0/16"],
            subnet_prefixes={
                "gateway": "10.3.0.0/24",
                "web": "10.3.1.0/24",
                "app": "10.3.2.0/24",
                "data": "10.3.3.0/24",
                "management": "10.3.4.0/24",
            },
            enable_ddos_protection=False,
            enable_firewall=False,
        ),
        security=SecuritySettings(
            enable_purge_protection=False,
            soft_delete_retention_days=14,
            enable_private_endpoints=False,
        ),
        monitoring=MonitoringSettings(
            log_retention_days=30,
            daily_quota_gb=2.0,
        ),
        features=FeatureFlags(
            enable_container_apps=True,
            enable_functions=True,
            enable_service_bus=True,
            enable_sql_database=True,
            enable_api_management=False,  # QA: no APIM needed
            enable_cdn=False,
            enable_data_factory=False,    # QA: minimal resources
            enable_redis_cache=False,
            enable_cosmos_db=False,
        ),
    ),
    "staging": EnvironmentSettings(
        name="staging",
        location="westus2",
        network=NetworkSettings(
            vnet_address_space=["10.1.0.0/16"],
            subnet_prefixes={
                "gateway": "10.1.0.0/24",
                "web": "10.1.1.0/24",
                "app": "10.1.2.0/24",
                "data": "10.1.3.0/24",
                "management": "10.1.4.0/24",
            },
            enable_ddos_protection=False,
            enable_firewall=False,
        ),
        security=SecuritySettings(
            enable_purge_protection=False,
            soft_delete_retention_days=30,
            enable_private_endpoints=True,
        ),
        monitoring=MonitoringSettings(
            log_retention_days=60,
            daily_quota_gb=5.0,
        ),
        features=FeatureFlags(
            enable_container_apps=True,
            enable_functions=True,
            enable_service_bus=True,
            enable_sql_database=True,
            enable_api_management=True,
            enable_cdn=True,              # Staging: test CDN before prod
            enable_data_factory=False,
            enable_redis_cache=False,
            enable_cosmos_db=False,
        ),
    ),
    "prod": EnvironmentSettings(
        name="prod",
        location="westus2",
        network=NetworkSettings(
            vnet_address_space=["10.2.0.0/16"],
            subnet_prefixes={
                "gateway": "10.2.0.0/24",
                "web": "10.2.1.0/24",
                "app": "10.2.2.0/24",
                "data": "10.2.3.0/24",
                "management": "10.2.4.0/24",
            },
            enable_ddos_protection=True,
            enable_firewall=True,
        ),
        security=SecuritySettings(
            enable_purge_protection=True,
            soft_delete_retention_days=90,
            enable_private_endpoints=True,
        ),
        monitoring=MonitoringSettings(
            log_retention_days=365,
            daily_quota_gb=None,  # No limit
        ),
        features=FeatureFlags(
            enable_container_apps=True,
            enable_functions=True,
            enable_service_bus=True,
            enable_sql_database=True,
            enable_api_management=True,
            enable_cdn=True,
            enable_data_factory=False,
            enable_redis_cache=True,      # Prod: caching for performance
            enable_cosmos_db=False,
        ),
    ),
}


def get_environment_settings(environment: Optional[str] = None) -> EnvironmentSettings:
    """
    Get settings for the specified environment.

    Args:
        environment: Environment name. If None, reads from Pulumi stack name.

    Returns:
        EnvironmentSettings for the environment

    Raises:
        ValueError: If environment is not recognized
    """
    if environment is None:
        # Infer from stack name
        stack_name = pulumi.get_stack()
        # Stack name might be 'org/project/dev' or just 'dev'
        environment = stack_name.split("/")[-1]

    if environment not in ENVIRONMENT_CONFIGS:
        raise ValueError(
            f"Unknown environment: {environment}. "
            f"Valid environments: {list(ENVIRONMENT_CONFIGS.keys())}"
        )

    return ENVIRONMENT_CONFIGS[environment]
