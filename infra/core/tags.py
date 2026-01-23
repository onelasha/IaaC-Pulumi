"""Tagging utilities for consistent resource tagging."""

from datetime import datetime, timezone
from typing import Optional
import pulumi


def get_default_tags(
    environment: str,
    component: Optional[str] = None,
    owner: Optional[str] = None,
    cost_center: Optional[str] = None,
) -> dict[str, str]:
    """
    Generate default tags for Azure resources.

    All resources should use these tags for:
    - Cost allocation and tracking
    - Environment identification
    - Ownership and accountability
    - Automation and compliance

    Args:
        environment: Environment name (dev, staging, prod)
        component: Component or application name
        owner: Team or individual owner
        cost_center: Cost center for billing

    Returns:
        Dictionary of tag key-value pairs
    """
    config = pulumi.Config()
    project = pulumi.get_project()
    stack = pulumi.get_stack()

    tags = {
        "Environment": environment,
        "ManagedBy": "Pulumi",
        "Project": project,
        "Stack": stack,
        "CreatedDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    if component:
        tags["Component"] = component

    if owner:
        tags["Owner"] = owner
    else:
        # Try to get from config
        owner_config = config.get("owner")
        if owner_config:
            tags["Owner"] = owner_config

    if cost_center:
        tags["CostCenter"] = cost_center
    else:
        # Try to get from config
        cc_config = config.get("costCenter")
        if cc_config:
            tags["CostCenter"] = cc_config

    return tags


def merge_tags(
    default_tags: dict[str, str],
    extra_tags: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """
    Merge extra tags with default tags.

    Extra tags take precedence over defaults.

    Args:
        default_tags: Base tags dictionary
        extra_tags: Additional tags to merge

    Returns:
        Merged tags dictionary
    """
    if extra_tags is None:
        return default_tags.copy()

    merged = default_tags.copy()
    merged.update(extra_tags)
    return merged
