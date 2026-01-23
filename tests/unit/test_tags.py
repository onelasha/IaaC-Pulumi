"""Unit tests for tagging utilities."""

import pytest
from unittest.mock import patch, MagicMock


class TestGetDefaultTags:
    """Tests for get_default_tags function."""

    @patch("infra.core.tags.pulumi")
    def test_required_tags_present(self, mock_pulumi: MagicMock) -> None:
        """Test that required tags are always present."""
        mock_pulumi.Config.return_value = MagicMock(get=MagicMock(return_value=None))
        mock_pulumi.get_project.return_value = "test-project"
        mock_pulumi.get_stack.return_value = "dev"

        from infra.core.tags import get_default_tags

        tags = get_default_tags(environment="dev")

        assert "Environment" in tags
        assert "ManagedBy" in tags
        assert "Project" in tags
        assert "Stack" in tags
        assert "CreatedDate" in tags

    @patch("infra.core.tags.pulumi")
    def test_environment_tag(self, mock_pulumi: MagicMock) -> None:
        """Test environment tag is set correctly."""
        mock_pulumi.Config.return_value = MagicMock(get=MagicMock(return_value=None))
        mock_pulumi.get_project.return_value = "test-project"
        mock_pulumi.get_stack.return_value = "prod"

        from infra.core.tags import get_default_tags

        tags = get_default_tags(environment="prod")

        assert tags["Environment"] == "prod"

    @patch("infra.core.tags.pulumi")
    def test_component_tag(self, mock_pulumi: MagicMock) -> None:
        """Test component tag when provided."""
        mock_pulumi.Config.return_value = MagicMock(get=MagicMock(return_value=None))
        mock_pulumi.get_project.return_value = "test-project"
        mock_pulumi.get_stack.return_value = "dev"

        from infra.core.tags import get_default_tags

        tags = get_default_tags(environment="dev", component="networking")

        assert tags["Component"] == "networking"

    @patch("infra.core.tags.pulumi")
    def test_managed_by_pulumi(self, mock_pulumi: MagicMock) -> None:
        """Test ManagedBy tag is set to Pulumi."""
        mock_pulumi.Config.return_value = MagicMock(get=MagicMock(return_value=None))
        mock_pulumi.get_project.return_value = "test-project"
        mock_pulumi.get_stack.return_value = "dev"

        from infra.core.tags import get_default_tags

        tags = get_default_tags(environment="dev")

        assert tags["ManagedBy"] == "Pulumi"


class TestMergeTags:
    """Tests for merge_tags function."""

    def test_merge_extra_tags(self) -> None:
        """Test merging extra tags with defaults."""
        from infra.core.tags import merge_tags

        default_tags = {"Environment": "dev", "ManagedBy": "Pulumi"}
        extra_tags = {"Team": "Platform", "CostCenter": "123"}

        result = merge_tags(default_tags, extra_tags)

        assert result["Environment"] == "dev"
        assert result["Team"] == "Platform"
        assert result["CostCenter"] == "123"

    def test_extra_tags_override(self) -> None:
        """Test that extra tags override defaults."""
        from infra.core.tags import merge_tags

        default_tags = {"Environment": "dev"}
        extra_tags = {"Environment": "staging"}

        result = merge_tags(default_tags, extra_tags)

        assert result["Environment"] == "staging"

    def test_none_extra_tags(self) -> None:
        """Test merge with None extra tags."""
        from infra.core.tags import merge_tags

        default_tags = {"Environment": "dev"}

        result = merge_tags(default_tags, None)

        assert result == {"Environment": "dev"}
