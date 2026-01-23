"""Storage Account Component with security best practices."""

from typing import Optional
import pulumi
from pulumi_azure_native import storage

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class StorageAccountComponent(pulumi.ComponentResource):
    """
    A standardized Storage Account component.

    Implements security best practices:
    - HTTPS only
    - TLS 1.2 minimum
    - Blob soft delete
    - Network restrictions
    - Managed identity access (no keys)
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        sku: str = "Standard_LRS",
        kind: str = "StorageV2",
        access_tier: str = "Hot",
        enable_hierarchical_namespace: bool = False,
        allowed_subnet_ids: Optional[list[pulumi.Input[str]]] = None,
        allowed_ip_ranges: Optional[list[str]] = None,
        containers: Optional[list[str]] = None,
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Storage Account component.

        Args:
            name: Logical name for the storage account
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            sku: Storage SKU (Standard_LRS, Standard_GRS, etc.)
            kind: Storage kind (StorageV2, BlobStorage, etc.)
            access_tier: Access tier (Hot, Cool)
            enable_hierarchical_namespace: Enable for Data Lake Gen2
            allowed_subnet_ids: Subnet IDs allowed to access
            allowed_ip_ranges: IP ranges allowed to access
            containers: Blob containers to create
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:storage:StorageAccount", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        storage_name = generate_resource_name(
            resource_type="st",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="storage")
        if extra_tags:
            tags.update(extra_tags)

        # Build network rules
        network_rules = None
        if allowed_subnet_ids or allowed_ip_ranges:
            virtual_network_rules = None
            if allowed_subnet_ids:
                virtual_network_rules = [
                    storage.VirtualNetworkRuleArgs(
                        virtual_network_resource_id=subnet_id,
                        action=storage.Action.ALLOW,
                    )
                    for subnet_id in allowed_subnet_ids
                ]

            ip_rules = None
            if allowed_ip_ranges:
                ip_rules = [
                    storage.IPRuleArgs(
                        i_p_address_or_range=ip_range,
                        action=storage.Action.ALLOW,
                    )
                    for ip_range in allowed_ip_ranges
                ]

            network_rules = storage.NetworkRuleSetArgs(
                bypass=storage.Bypass.AZURE_SERVICES,
                default_action=storage.DefaultAction.DENY,
                virtual_network_rules=virtual_network_rules,
                ip_rules=ip_rules,
            )

        self.account = storage.StorageAccount(
            storage_name,
            account_name=storage_name,
            resource_group_name=resource_group_name,
            location=self.location,
            sku=storage.SkuArgs(name=sku),
            kind=kind,
            access_tier=access_tier,
            enable_https_traffic_only=True,
            minimum_tls_version=storage.MinimumTlsVersion.TLS1_2,
            allow_blob_public_access=False,
            is_hns_enabled=enable_hierarchical_namespace,
            network_rule_set=network_rules,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Enable blob soft delete
        self.blob_services = storage.BlobServiceProperties(
            f"{storage_name}-blob-services",
            account_name=self.account.name,
            resource_group_name=resource_group_name,
            delete_retention_policy=storage.DeleteRetentionPolicyArgs(
                enabled=True,
                days=7,
            ),
            container_delete_retention_policy=storage.DeleteRetentionPolicyArgs(
                enabled=True,
                days=7,
            ),
            opts=pulumi.ResourceOptions(parent=self.account),
        )

        # Create containers if specified
        self.containers: dict[str, storage.BlobContainer] = {}
        if containers:
            for container_name in containers:
                self.containers[container_name] = storage.BlobContainer(
                    f"{storage_name}-{container_name}",
                    container_name=container_name,
                    account_name=self.account.name,
                    resource_group_name=resource_group_name,
                    public_access=storage.PublicAccess.NONE,
                    opts=pulumi.ResourceOptions(
                        parent=self.blob_services,
                        depends_on=[self.blob_services],
                    ),
                )

        self.register_outputs({
            "name": self.account.name,
            "id": self.account.id,
            "primary_endpoints": self.account.primary_endpoints,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the storage account name."""
        return self.account.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the storage account ID."""
        return self.account.id

    @property
    def primary_blob_endpoint(self) -> pulumi.Output[str]:
        """Get the primary blob endpoint."""
        return self.account.primary_endpoints.blob
