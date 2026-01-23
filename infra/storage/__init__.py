"""
Storage Infrastructure Module.

Contains Storage Account and Blob Container components.
"""

from .storage_account import StorageAccountComponent
from .stack import StorageStack

__all__ = [
    "StorageAccountComponent",
    "StorageStack",
]
