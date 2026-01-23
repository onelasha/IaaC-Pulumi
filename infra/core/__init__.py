"""
Core Infrastructure Module.

Contains foundational resources like resource groups and tagging utilities.
"""

from .resource_group import ResourceGroupComponent
from .tags import get_default_tags
from .naming import generate_resource_name
from .stack import CoreStack

__all__ = [
    "ResourceGroupComponent",
    "get_default_tags",
    "generate_resource_name",
    "CoreStack",
]
