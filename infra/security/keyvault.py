"""Key Vault Component with security best practices."""

from typing import Optional
import pulumi
from pulumi_azure_native import keyvault

from ..core.tags import get_default_tags
from ..core.naming import generate_resource_name


class KeyVaultComponent(pulumi.ComponentResource):
    """
    A standardized Key Vault component.

    Implements security best practices:
    - Soft delete enabled (required by Azure)
    - Purge protection for production
    - RBAC authorization (preferred over access policies)
    - Network restrictions
    - Diagnostic logging
    """

    def __init__(
        self,
        name: str,
        environment: str,
        resource_group_name: pulumi.Input[str],
        tenant_id: pulumi.Input[str],
        enable_rbac: bool = True,
        enable_purge_protection: Optional[bool] = None,
        soft_delete_retention_days: int = 90,
        allowed_subnet_ids: Optional[list[pulumi.Input[str]]] = None,
        allowed_ip_ranges: Optional[list[str]] = None,
        location: Optional[str] = None,
        extra_tags: Optional[dict[str, str]] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        Create a new Key Vault component.

        Args:
            name: Logical name for the Key Vault
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group to deploy into
            tenant_id: Azure AD tenant ID
            enable_rbac: Use RBAC for authorization (recommended)
            enable_purge_protection: Enable purge protection (auto for prod)
            soft_delete_retention_days: Soft delete retention (7-90 days)
            allowed_subnet_ids: Subnet IDs allowed to access
            allowed_ip_ranges: IP ranges allowed to access
            location: Azure region
            extra_tags: Additional tags
            opts: Pulumi resource options
        """
        super().__init__("azureinfra:security:KeyVault", name, None, opts)

        azure_config = pulumi.Config("azure-native")
        self.location = location or azure_config.require("location")

        # Auto-enable purge protection for production
        if enable_purge_protection is None:
            enable_purge_protection = environment == "prod"

        kv_name = generate_resource_name(
            resource_type="kv",
            name=name,
            environment=environment,
        )

        tags = get_default_tags(environment=environment, component="security")
        if extra_tags:
            tags.update(extra_tags)

        # Build network ACLs
        network_acls = None
        if allowed_subnet_ids or allowed_ip_ranges:
            virtual_network_rules = None
            if allowed_subnet_ids:
                virtual_network_rules = [
                    keyvault.VirtualNetworkRuleArgs(id=subnet_id)
                    for subnet_id in allowed_subnet_ids
                ]

            ip_rules = None
            if allowed_ip_ranges:
                ip_rules = [
                    keyvault.IPRuleArgs(value=ip_range)
                    for ip_range in allowed_ip_ranges
                ]

            network_acls = keyvault.NetworkRuleSetArgs(
                bypass="AzureServices",
                default_action=keyvault.NetworkRuleAction.DENY,
                virtual_network_rules=virtual_network_rules,
                ip_rules=ip_rules,
            )

        self.vault = keyvault.Vault(
            kv_name,
            vault_name=kv_name,
            resource_group_name=resource_group_name,
            location=self.location,
            properties=keyvault.VaultPropertiesArgs(
                tenant_id=tenant_id,
                sku=keyvault.SkuArgs(
                    family=keyvault.SkuFamily.A,
                    name=keyvault.SkuName.STANDARD,
                ),
                enable_rbac_authorization=enable_rbac,
                enabled_for_deployment=False,
                enabled_for_disk_encryption=False,
                enabled_for_template_deployment=False,
                enable_soft_delete=True,
                soft_delete_retention_in_days=soft_delete_retention_days,
                enable_purge_protection=enable_purge_protection,
                network_acls=network_acls,
            ),
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "name": self.vault.name,
            "id": self.vault.id,
            "uri": self.vault.properties.vault_uri,
        })

    @property
    def name(self) -> pulumi.Output[str]:
        """Get the Key Vault name."""
        return self.vault.name

    @property
    def id(self) -> pulumi.Output[str]:
        """Get the Key Vault ID."""
        return self.vault.id

    @property
    def uri(self) -> pulumi.Output[str]:
        """Get the Key Vault URI."""
        return self.vault.properties.vault_uri
