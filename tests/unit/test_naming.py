"""Unit tests for naming conventions."""

import pytest
from unittest.mock import patch, MagicMock


class TestGenerateResourceName:
    """Tests for generate_resource_name function."""

    @patch("infra.core.naming.pulumi")
    def test_resource_group_naming(self, mock_pulumi: MagicMock) -> None:
        """Test resource group naming convention."""
        mock_pulumi.Config.return_value = MagicMock()

        from infra.core.naming import generate_resource_name

        name = generate_resource_name(
            resource_type="rg",
            name="webapp",
            environment="dev",
        )

        assert name == "rg-webapp-dev"
        assert len(name) <= 90  # Azure limit

    @patch("infra.core.naming.pulumi")
    def test_storage_account_naming(self, mock_pulumi: MagicMock) -> None:
        """Test storage account naming (lowercase, no hyphens)."""
        mock_pulumi.Config.return_value = MagicMock()

        from infra.core.naming import generate_resource_name

        name = generate_resource_name(
            resource_type="st",
            name="app",
            environment="dev",
        )

        assert name == "stappdev"
        assert name.islower()
        assert "-" not in name
        assert len(name) <= 24  # Azure limit

    @patch("infra.core.naming.pulumi")
    def test_keyvault_naming(self, mock_pulumi: MagicMock) -> None:
        """Test Key Vault naming convention."""
        mock_pulumi.Config.return_value = MagicMock()

        from infra.core.naming import generate_resource_name

        name = generate_resource_name(
            resource_type="kv",
            name="secrets",
            environment="prod",
        )

        assert name == "kv-secrets-prod"
        assert len(name) <= 24  # Azure limit

    @patch("infra.core.naming.pulumi")
    def test_name_with_region_code(self, mock_pulumi: MagicMock) -> None:
        """Test naming with region code."""
        mock_pulumi.Config.return_value = MagicMock()

        from infra.core.naming import generate_resource_name

        name = generate_resource_name(
            resource_type="rg",
            name="webapp",
            environment="dev",
            region_code="wus2",
        )

        assert name == "rg-webapp-dev-wus2"

    @patch("infra.core.naming.pulumi")
    def test_name_with_instance(self, mock_pulumi: MagicMock) -> None:
        """Test naming with instance number."""
        mock_pulumi.Config.return_value = MagicMock()

        from infra.core.naming import generate_resource_name

        name = generate_resource_name(
            resource_type="vm",
            name="web",
            environment="prod",
            instance="001",
        )

        assert name == "vm-web-prod-001"


class TestGetRegionCode:
    """Tests for get_region_code function."""

    def test_common_regions(self) -> None:
        """Test common Azure region codes."""
        from infra.core.naming import get_region_code

        assert get_region_code("westus2") == "wus2"
        assert get_region_code("eastus") == "eus"
        assert get_region_code("westeurope") == "weu"
        assert get_region_code("northeurope") == "neu"

    def test_unknown_region(self) -> None:
        """Test fallback for unknown regions."""
        from infra.core.naming import get_region_code

        # Unknown regions should return first 4 chars
        assert get_region_code("unknownregion") == "unkn"
