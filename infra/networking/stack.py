"""Networking Stack - Network infrastructure setup."""

from typing import Optional
import pulumi

from .vnet import VNetComponent, SubnetConfig
from .nsg import NetworkSecurityGroupComponent, get_web_tier_rules


class NetworkingStack:
    """
    Networking infrastructure stack.

    Creates hub-spoke or standalone VNet topology with proper
    subnet segmentation and network security groups.
    """

    def __init__(
        self,
        environment: str,
        resource_group_name: pulumi.Input[str],
        address_space: Optional[list[str]] = None,
        config: Optional[pulumi.Config] = None,
    ):
        """
        Initialize the networking stack.

        Args:
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group for network resources
            address_space: VNet address space (defaults based on environment)
            config: Optional Pulumi config
        """
        self.environment = environment
        self.config = config or pulumi.Config()
        self.resource_group_name = resource_group_name

        # Default address spaces per environment
        default_address_spaces = {
            "dev": ["10.0.0.0/16"],
            "staging": ["10.1.0.0/16"],
            "prod": ["10.2.0.0/16"],
        }

        self.address_space = address_space or default_address_spaces.get(
            environment, ["10.0.0.0/16"]
        )

        self._create_network_resources()

    def _create_network_resources(self) -> None:
        """Create network resources."""

        # Define subnets with proper segmentation
        base_prefix = self.address_space[0].rsplit(".", 2)[0]  # e.g., "10.0"

        subnets = [
            SubnetConfig(
                name="gateway",
                address_prefix=f"{base_prefix}.0.0/24",
                service_endpoints=["Microsoft.KeyVault"],
            ),
            SubnetConfig(
                name="web",
                address_prefix=f"{base_prefix}.1.0/24",
                service_endpoints=[
                    "Microsoft.KeyVault",
                    "Microsoft.Storage",
                ],
            ),
            SubnetConfig(
                name="app",
                address_prefix=f"{base_prefix}.2.0/24",
                service_endpoints=[
                    "Microsoft.KeyVault",
                    "Microsoft.Storage",
                    "Microsoft.Sql",
                ],
            ),
            SubnetConfig(
                name="data",
                address_prefix=f"{base_prefix}.3.0/24",
                service_endpoints=[
                    "Microsoft.KeyVault",
                    "Microsoft.Storage",
                ],
                private_endpoint_network_policies="Disabled",
            ),
            SubnetConfig(
                name="management",
                address_prefix=f"{base_prefix}.4.0/24",
                service_endpoints=["Microsoft.KeyVault"],
            ),
        ]

        # Create main VNet
        self.vnet = VNetComponent(
            name="main",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            address_space=self.address_space,
            subnets=subnets,
        )

        # Create NSGs for each tier
        self.web_nsg = NetworkSecurityGroupComponent(
            name="web",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            rules=get_web_tier_rules(),
        )

        self.app_nsg = NetworkSecurityGroupComponent(
            name="app",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
        )

        self.data_nsg = NetworkSecurityGroupComponent(
            name="data",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
        )

    def export_outputs(self) -> dict[str, pulumi.Output]:
        """Export stack outputs."""
        outputs = {
            "vnet_name": self.vnet.name,
            "vnet_id": self.vnet.id,
            "web_nsg_id": self.web_nsg.id,
            "app_nsg_id": self.app_nsg.id,
            "data_nsg_id": self.data_nsg.id,
        }

        for name, value in outputs.items():
            pulumi.export(name, value)

        return outputs
