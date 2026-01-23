"""Virtual Network Component with standardized configuration."""

from typing import Optional
import pulumi
from pulumi_azure_native import network

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class SubnetConfig:
    """Configuration for a subnet within a VNet."""

    def __init__(
        self,
        name: str,
        address_prefix: str,
        service_endpoints: Optional[list[str]] = None,
        delegation: Optional[str] = None,
        private_endpoint_network_policies: str = "Enabled",
    ):
        """
        Configure a subnet.

        Args:
            name: Subnet name (e.g., 'app', 'data', 'gateway')
            address_prefix: CIDR block (e.g., '10.0.1.0/24')
            service_endpoints: List of service endpoints to enable
            delegation: Service delegation (e.g., 'Microsoft.Web/serverFarms')
            private_endpoint_network_policies: Enable/Disable private endpoint policies
        """
        self.name = name
        self.address_prefix = address_prefix
        self.service_endpoints = service_endpoints or []
        self.delegation = delegation
        self.private_endpoint_network_policies = private_endpoint_network_policies


class VNetComponent(pulumi.ComponentResource):
    """
    A standardized Virtual Network component.

    Creates a VNet with subnets following security best practices:
    - Proper subnet segmentation
    - Service endpoints for Azure services
    - Support for private endpoints
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        address_space: list[str],
        subnets: list[SubnetConfig],
        location: Optional[str] = None,
        dns_servers: Optional[list[str]] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Virtual Network component.

        Args:
            name: Logical name for the VNet
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            address_space: List of CIDR blocks for the VNet
            subnets: List of subnet configurations
            location: Azure region
            dns_servers: Custom DNS servers
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:networking:VNet", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")
        self.environment = environment

        vnet_name = generate_resource_name(
            resource_type="vnet",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="networking")
        if extra_tags:
            tags.update(extra_tags)

        # Build subnet configurations
        subnet_args = []
        for subnet_config in subnets:
            subnet_name = generate_resource_name(
                resource_type="snet",
                name=subnet_config.name,
                environment=environment,
            )

            subnet_arg = network.SubnetArgs(
                name=subnet_name,
                address_prefix=subnet_config.address_prefix,
                private_endpoint_network_policies=subnet_config.private_endpoint_network_policies,
            )

            # Add service endpoints if specified
            if subnet_config.service_endpoints:
                subnet_arg = network.SubnetArgs(
                    name=subnet_name,
                    address_prefix=subnet_config.address_prefix,
                    private_endpoint_network_policies=subnet_config.private_endpoint_network_policies,
                    service_endpoints=[
                        network.ServiceEndpointPropertiesFormatArgs(service=svc)
                        for svc in subnet_config.service_endpoints
                    ],
                )

            subnet_args.append(subnet_arg)

        # Create the VNet
        self.vnet = network.VirtualNetwork(
            vnet_name,
            virtual_network_name=vnet_name,
            resource_group_name=resource_group_name,
            location=self.location,
            address_space=network.AddressSpaceArgs(
                address_prefixes=address_space,
            ),
            subnets=subnet_args,
            dhcp_options=network.DhcpOptionsArgs(
                dns_servers=dns_servers,
            ) if dns_servers else None,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Store subnet references
        self.subnets: dict[str, pulumi.Output[str]] = {}
        for i, subnet_config in enumerate(subnets):
            self.subnets[subnet_config.name] = self.vnet.subnets.apply(
                lambda s, idx=i: s[idx].id if s and len(s) > idx else ""
            )

        self.register_outputs({
            "name": self.vnet.name,
            "id": self.vnet.id,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the VNet name."""
        return self.vnet.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the VNet ID."""
        return self.vnet.id

    def get_subnet_id(self, subnet_name: str) -> pulumi.Output[str]:
        """Get a subnet ID by logical name."""
        return self.subnets.get(subnet_name, pulumi.Output.from_input(""))
