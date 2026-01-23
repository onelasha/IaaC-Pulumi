"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_azure_config():
    """Fixture providing mock Azure configuration."""
    return {
        "location": "westus2",
        "subscription_id": "00000000-0000-0000-0000-000000000000",
        "tenant_id": "00000000-0000-0000-0000-000000000000",
    }


@pytest.fixture
def mock_environment():
    """Fixture providing mock environment settings."""
    return "dev"
