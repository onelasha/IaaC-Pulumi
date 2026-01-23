"""Naming convention utilities for Azure resources."""

import pulumi
from typing import Optional


# Azure resource naming constraints
RESOURCE_NAME_LIMITS = {
    "rg": {"max_length": 90, "prefix": "rg"},
    "st": {"max_length": 24, "prefix": "st", "lowercase": True, "no_hyphens": True},
    "kv": {"max_length": 24, "prefix": "kv"},
    "vnet": {"max_length": 64, "prefix": "vnet"},
    "snet": {"max_length": 80, "prefix": "snet"},
    "nsg": {"max_length": 80, "prefix": "nsg"},
    "pip": {"max_length": 80, "prefix": "pip"},
    "nic": {"max_length": 80, "prefix": "nic"},
    "vm": {"max_length": 64, "prefix": "vm"},
    "aks": {"max_length": 63, "prefix": "aks"},
    "acr": {"max_length": 50, "prefix": "acr", "lowercase": True, "no_hyphens": True},
    "law": {"max_length": 63, "prefix": "law"},
    "appi": {"max_length": 260, "prefix": "appi"},
    "id": {"max_length": 128, "prefix": "id"},
    "sql": {"max_length": 63, "prefix": "sql"},
    "psql": {"max_length": 63, "prefix": "psql"},
}


def generate_resource_name(
    resource_type: str,
    name: str,
    environment: str,
    region_code: Optional[str] = None,
    instance: Optional[str] = None,
) -> str:
    """
    Generate a standardized resource name following Azure naming conventions.

    Format: {prefix}-{name}-{environment}-{region}-{instance}

    Example: rg-webapp-dev-wus2-001

    Args:
        resource_type: Resource type code (rg, st, kv, vnet, etc.)
        name: Logical resource name
        environment: Environment (dev, staging, prod)
        region_code: Optional region code (e.g., 'wus2' for West US 2)
        instance: Optional instance number or identifier

    Returns:
        Formatted resource name

    Raises:
        ValueError: If resource type is unknown or name exceeds limits
    """
    config = pulumi.Config()

    if resource_type not in RESOURCE_NAME_LIMITS:
        # Use generic naming for unknown types
        limits = {"max_length": 80, "prefix": resource_type}
    else:
        limits = RESOURCE_NAME_LIMITS[resource_type]

    # Build name parts
    parts = [limits["prefix"], name, environment]

    if region_code:
        parts.append(region_code)

    if instance:
        parts.append(instance)

    # Determine separator
    separator = "" if limits.get("no_hyphens") else "-"
    full_name = separator.join(parts)

    # Apply transformations
    if limits.get("lowercase"):
        full_name = full_name.lower()

    # Truncate if necessary
    max_length = limits["max_length"]
    if len(full_name) > max_length:
        full_name = full_name[:max_length]

    return full_name


def get_region_code(location: str) -> str:
    """
    Convert Azure region name to short code.

    Args:
        location: Azure region name (e.g., 'westus2')

    Returns:
        Short region code (e.g., 'wus2')
    """
    region_codes = {
        "westus": "wus",
        "westus2": "wus2",
        "westus3": "wus3",
        "eastus": "eus",
        "eastus2": "eus2",
        "centralus": "cus",
        "northcentralus": "ncus",
        "southcentralus": "scus",
        "westcentralus": "wcus",
        "canadacentral": "cac",
        "canadaeast": "cae",
        "brazilsouth": "brs",
        "northeurope": "neu",
        "westeurope": "weu",
        "uksouth": "uks",
        "ukwest": "ukw",
        "francecentral": "frc",
        "francesouth": "frs",
        "germanywestcentral": "gwc",
        "norwayeast": "noe",
        "switzerlandnorth": "chn",
        "uaenorth": "uan",
        "southafricanorth": "san",
        "australiaeast": "aue",
        "australiasoutheast": "ause",
        "australiacentral": "auc",
        "eastasia": "ea",
        "southeastasia": "sea",
        "japaneast": "jpe",
        "japanwest": "jpw",
        "koreacentral": "krc",
        "koreasouth": "krs",
        "centralindia": "inc",
        "southindia": "ins",
        "westindia": "inw",
    }

    normalized = location.lower().replace(" ", "").replace("-", "")
    return region_codes.get(normalized, location[:4])
