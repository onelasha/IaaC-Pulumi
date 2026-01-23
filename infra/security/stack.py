"""Security Stack - Security infrastructure setup."""

from typing import Optional
import pulumi
from pulumi_azure_native import authorization

from .keyvault import KeyVaultComponent
from .managed_identity import ManagedIdentityComponent


class SecurityStack:
    """
    Security infrastructure stack.

    Creates Key Vaults, Managed Identities, and RBAC assignments
    following zero-trust security principles.
    """

    def __init__(
        self,
        environment: str,
        resource_group_name: pulumi.Input[str],
        tenant_id: pulumi.Input[str],
        config: Optional[pulumi.Config] = None,
    ):
        """
        Initialize the security stack.

        Args:
            environment: Environment name (dev, staging, prod)
            resource_group_name: Resource group for security resources
            tenant_id: Azure AD tenant ID
            config: Optional Pulumi config
        """
        self.environment = environment
        self.config = config or pulumi.Config()
        self.resource_group_name = resource_group_name
        self.tenant_id = tenant_id

        self._create_security_resources()

    def _create_security_resources(self) -> None:
        """Create security resources."""

        # Create main Key Vault for secrets
        self.key_vault = KeyVaultComponent(
            name="main",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
            tenant_id=self.tenant_id,
            enable_rbac=True,
        )

        # Create managed identity for applications
        self.app_identity = ManagedIdentityComponent(
            name="app",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
        )

        # Create managed identity for data access
        self.data_identity = ManagedIdentityComponent(
            name="data",
            environment=self.environment,
            resource_group_name=self.resource_group_name,
        )

    def export_outputs(self) -> dict[str, pulumi.Output]:
        """Export stack outputs."""
        outputs = {
            "key_vault_name": self.key_vault.name,
            "key_vault_uri": self.key_vault.uri,
            "app_identity_id": self.app_identity.id,
            "app_identity_principal_id": self.app_identity.principal_id,
            "app_identity_client_id": self.app_identity.client_id,
            "data_identity_id": self.data_identity.id,
            "data_identity_principal_id": self.data_identity.principal_id,
        }

        for name, value in outputs.items():
            pulumi.export(name, value)

        return outputs
