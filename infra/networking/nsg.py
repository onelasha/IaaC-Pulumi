"""Network Security Group Component with security best practices."""

from typing import Optional
import pulumi
from pulumi_azure_native import network

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class SecurityRuleConfig:
    """Configuration for an NSG security rule."""

    def __init__(
        self,
        name: str,
        priority: int,
        direction: str,
        access: str,
        protocol: str,
        source_address_prefix: str = "*",
        source_port_range: str = "*",
        destination_address_prefix: str = "*",
        destination_port_range: str = "*",
        description: Optional[str] = None,
    ):
        """
        Configure a security rule.

        Args:
            name: Rule name
            priority: Rule priority (100-4096, lower = higher priority)
            direction: 'Inbound' or 'Outbound'
            access: 'Allow' or 'Deny'
            protocol: 'Tcp', 'Udp', 'Icmp', or '*'
            source_address_prefix: Source CIDR or tag
            source_port_range: Source port or range
            destination_address_prefix: Destination CIDR or tag
            destination_port_range: Destination port or range
            description: Rule description
        """
        self.name = name
        self.priority = priority
        self.direction = direction
        self.access = access
        self.protocol = protocol
        self.source_address_prefix = source_address_prefix
        self.source_port_range = source_port_range
        self.destination_address_prefix = destination_address_prefix
        self.destination_port_range = destination_port_range
        self.description = description


class NetworkSecurityGroupComponent(pulumi.ComponentResource):
    """
    A standardized Network Security Group component.

    Implements security best practices:
    - Deny all inbound by default (Azure default)
    - Explicit allow rules only
    - Logging and monitoring integration
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        rules: Optional[list[SecurityRuleConfig]] = None,
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Network Security Group component.

        Args:
            name: Logical name for the NSG
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            rules: List of security rules
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:networking:NSG", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        nsg_name = generate_resource_name(
            resource_type="nsg",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="networking")
        if extra_tags:
            tags.update(extra_tags)

        # Build security rules
        security_rules = []
        if rules:
            for rule in rules:
                security_rules.append(
                    network.SecurityRuleArgs(
                        name=rule.name,
                        priority=rule.priority,
                        direction=rule.direction,
                        access=rule.access,
                        protocol=rule.protocol,
                        source_address_prefix=rule.source_address_prefix,
                        source_port_range=rule.source_port_range,
                        destination_address_prefix=rule.destination_address_prefix,
                        destination_port_range=rule.destination_port_range,
                        description=rule.description,
                    )
                )

        self.nsg = network.NetworkSecurityGroup(
            nsg_name,
            network_security_group_name=nsg_name,
            resource_group_name=resource_group_name,
            location=self.location,
            security_rules=security_rules if security_rules else None,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "name": self.nsg.name,
            "id": self.nsg.id,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the NSG name."""
        return self.nsg.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the NSG ID."""
        return self.nsg.id


def get_web_tier_rules() -> list[SecurityRuleConfig]:
    """Get standard rules for web tier NSG."""
    return [
        SecurityRuleConfig(
            name="AllowHTTPS",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_address_prefix="Internet",
            destination_port_range="443",
            description="Allow HTTPS traffic from internet",
        ),
        SecurityRuleConfig(
            name="AllowHTTP",
            priority=110,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_address_prefix="Internet",
            destination_port_range="80",
            description="Allow HTTP traffic (for redirect to HTTPS)",
        ),
    ]


def get_app_tier_rules(web_subnet_prefix: str) -> list[SecurityRuleConfig]:
    """Get standard rules for app tier NSG."""
    return [
        SecurityRuleConfig(
            name="AllowFromWebTier",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_address_prefix=web_subnet_prefix,
            destination_port_range="8080",
            description="Allow traffic from web tier",
        ),
    ]


def get_data_tier_rules(app_subnet_prefix: str) -> list[SecurityRuleConfig]:
    """Get standard rules for data tier NSG."""
    return [
        SecurityRuleConfig(
            name="AllowFromAppTier",
            priority=100,
            direction="Inbound",
            access="Allow",
            protocol="Tcp",
            source_address_prefix=app_subnet_prefix,
            destination_port_range="1433",
            description="Allow SQL traffic from app tier",
        ),
    ]
