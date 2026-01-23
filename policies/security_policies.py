"""
Security Policies for Azure Resources.

These policies enforce security best practices and compliance requirements.
Run with: pulumi preview --policy-pack ./policies
"""

from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)


def storage_https_only_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure storage accounts only allow HTTPS traffic."""
    if args.resource_type == "azure-native:storage:StorageAccount":
        props = args.props
        if props.get("enableHttpsTrafficOnly") is False:
            report_violation("Storage accounts must enforce HTTPS-only traffic.")


def storage_tls_version_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure storage accounts use TLS 1.2 or higher."""
    if args.resource_type == "azure-native:storage:StorageAccount":
        props = args.props
        tls_version = props.get("minimumTlsVersion", "")
        if tls_version and tls_version not in ["TLS1_2", "TLS1_3"]:
            report_violation(
                f"Storage accounts must use TLS 1.2 or higher. Found: {tls_version}"
            )


def storage_public_access_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure storage accounts disable public blob access."""
    if args.resource_type == "azure-native:storage:StorageAccount":
        props = args.props
        if props.get("allowBlobPublicAccess") is True:
            report_violation(
                "Storage accounts must not allow public blob access."
            )


def keyvault_purge_protection_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure Key Vaults have purge protection enabled in production."""
    if args.resource_type == "azure-native:keyvault:Vault":
        props = args.props
        vault_props = props.get("properties", {})
        # Check if this is a production resource by tags
        tags = props.get("tags", {})
        if tags.get("Environment") == "prod":
            if vault_props.get("enablePurgeProtection") is not True:
                report_violation(
                    "Production Key Vaults must have purge protection enabled."
                )


def keyvault_soft_delete_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure Key Vaults have soft delete enabled."""
    if args.resource_type == "azure-native:keyvault:Vault":
        props = args.props
        vault_props = props.get("properties", {})
        if vault_props.get("enableSoftDelete") is False:
            report_violation("Key Vaults must have soft delete enabled.")


def require_tags_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure all resources have required tags."""
    # Resources that support tags
    taggable_types = [
        "azure-native:resources:ResourceGroup",
        "azure-native:storage:StorageAccount",
        "azure-native:keyvault:Vault",
        "azure-native:network:VirtualNetwork",
        "azure-native:network:NetworkSecurityGroup",
        "azure-native:operationalinsights:Workspace",
        "azure-native:insights:Component",
    ]

    if args.resource_type in taggable_types:
        tags = args.props.get("tags", {})
        required_tags = ["Environment", "ManagedBy", "Project"]

        missing_tags = [tag for tag in required_tags if tag not in tags]
        if missing_tags:
            report_violation(
                f"Resource is missing required tags: {', '.join(missing_tags)}"
            )


def nsg_no_open_to_internet_validator(
    args: ResourceValidationArgs,
    report_violation: callable,
) -> None:
    """Ensure NSGs don't have rules allowing all traffic from internet."""
    if args.resource_type == "azure-native:network:NetworkSecurityGroup":
        props = args.props
        rules = props.get("securityRules", [])

        for rule in rules:
            if (
                rule.get("access") == "Allow"
                and rule.get("direction") == "Inbound"
                and rule.get("sourceAddressPrefix") in ["*", "0.0.0.0/0", "Internet"]
                and rule.get("destinationPortRange") == "*"
            ):
                report_violation(
                    f"NSG rule '{rule.get('name')}' allows all inbound traffic "
                    "from the internet. This is a security risk."
                )


# Create the policy pack
security_policies = PolicyPack(
    name="azure-security-policies",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        ResourceValidationPolicy(
            name="storage-https-only",
            description="Storage accounts must enforce HTTPS-only traffic",
            validate=storage_https_only_validator,
        ),
        ResourceValidationPolicy(
            name="storage-tls-version",
            description="Storage accounts must use TLS 1.2 or higher",
            validate=storage_tls_version_validator,
        ),
        ResourceValidationPolicy(
            name="storage-no-public-access",
            description="Storage accounts must not allow public blob access",
            validate=storage_public_access_validator,
        ),
        ResourceValidationPolicy(
            name="keyvault-purge-protection",
            description="Production Key Vaults must have purge protection enabled",
            validate=keyvault_purge_protection_validator,
        ),
        ResourceValidationPolicy(
            name="keyvault-soft-delete",
            description="Key Vaults must have soft delete enabled",
            validate=keyvault_soft_delete_validator,
        ),
        ResourceValidationPolicy(
            name="required-tags",
            description="Resources must have required tags",
            validate=require_tags_validator,
        ),
        ResourceValidationPolicy(
            name="nsg-no-open-to-internet",
            description="NSGs must not allow all inbound traffic from internet",
            validate=nsg_no_open_to_internet_validator,
        ),
    ],
)
