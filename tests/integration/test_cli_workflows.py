"""Integration tests for CLI end-to-end workflows."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest
import yaml
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.exceptions import ConfigError
from easel.config.manager import ConfigManager
from easel.config.models import CanvasInstance, EaselConfig


class TestConfigurationWorkflow:
    """Test complete configuration setup workflow."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_canvas_response(self):
        """Mock successful Canvas API response."""
        return {
            "id": 123,
            "name": "Test User",
            "email": "test@university.edu",
            "login_id": "testuser",
        }

    def test_init_command_interactive_setup(self, runner, temp_config_dir, mock_canvas_response):
        """Test interactive configuration setup."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = mock_canvas_response
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                # Simulate user input
                user_input = "\n".join([
                    "Test University",  # institution name
                    "https://test.instructure.com",  # canvas URL
                    "test_token_123",  # API token
                    "y",  # confirm token verification
                ])

                result = runner.invoke(cli, ["init"], input=user_input)

                assert result.exit_code == 0
                assert "Configuration saved successfully" in result.output
                assert (temp_config_dir / "config.yaml").exists()

                # Verify configuration content
                with open(temp_config_dir / "config.yaml") as f:
                    config_data = yaml.safe_load(f)
                
                assert config_data["canvas"]["name"] == "Test University"
                assert config_data["canvas"]["base_url"] == "https://test.instructure.com"

    def test_init_command_with_invalid_token(self, runner, temp_config_dir):
        """Test init command with invalid API token."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock failed API verification
                mock_response = AsyncMock()
                mock_response.is_success = False
                mock_response.status_code = 401
                mock_response.json.return_value = {"message": "Invalid token"}
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                user_input = "\n".join([
                    "Test University",
                    "https://test.instructure.com",
                    "invalid_token",
                    "n",  # don't save after failed verification
                ])

                result = runner.invoke(cli, ["init"], input=user_input)

                assert result.exit_code == 1
                assert "Token verification failed" in result.output
                assert not (temp_config_dir / "config.yaml").exists()

    def test_config_list_command(self, runner, temp_config_dir):
        """Test config list command with existing configuration."""
        # Create test configuration
        config = EaselConfig(
            canvas=CanvasInstance(
                name="Test University",
                base_url="https://test.instructure.com",
                api_token="test_token",
            )
        )

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config.model_dump(), f)

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["config", "list"])

            assert result.exit_code == 0
            assert "Test University" in result.output
            assert "https://test.instructure.com" in result.output

    def test_config_list_no_configuration(self, runner, temp_config_dir):
        """Test config list command with no configuration."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["config", "list"])

            assert result.exit_code == 1
            assert "No configuration found" in result.output


class TestDoctorCommand:
    """Test doctor command diagnostic workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    @pytest.fixture
    def valid_config(self, temp_config_dir):
        """Create valid configuration."""
        config = EaselConfig(
            canvas=CanvasInstance(
                name="Test University",
                base_url="https://test.instructure.com",
                api_token="test_token",
            )
        )

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config.model_dump(), f)
        
        return config

    def test_doctor_all_checks_pass(self, runner, temp_config_dir, valid_config):
        """Test doctor command when all checks pass."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = {"id": 123, "name": "Test User"}
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                result = runner.invoke(cli, ["doctor"])

                assert result.exit_code == 0
                assert "✓ Configuration file found" in result.output
                assert "✓ Configuration validation passed" in result.output
                assert "✓ Canvas API connection successful" in result.output
                assert "All checks passed!" in result.output

    def test_doctor_missing_configuration(self, runner, temp_config_dir):
        """Test doctor command with missing configuration."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["doctor"])

            assert result.exit_code == 1
            assert "✗ Configuration file not found" in result.output
            assert "Run 'easel init' to create configuration" in result.output

    def test_doctor_invalid_configuration(self, runner, temp_config_dir):
        """Test doctor command with invalid configuration."""
        # Create invalid configuration file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content:")

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["doctor"])

            assert result.exit_code == 1
            assert "✗ Configuration validation failed" in result.output

    def test_doctor_api_connection_failure(self, runner, temp_config_dir, valid_config):
        """Test doctor command with API connection failure."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock failed API connection
                mock_response = AsyncMock()
                mock_response.is_success = False
                mock_response.status_code = 401
                mock_response.json.return_value = {"message": "Unauthorized"}
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                result = runner.invoke(cli, ["doctor"])

                assert result.exit_code == 1
                assert "✗ Canvas API connection failed" in result.output


class TestOutputFormats:
    """Test different output format workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    @pytest.fixture
    def valid_config(self, temp_config_dir):
        """Create valid configuration."""
        config = EaselConfig(
            canvas=CanvasInstance(
                name="Test University",
                base_url="https://test.instructure.com",
                api_token="test_token",
            )
        )

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config.model_dump(), f)
        
        return config

    def test_config_list_json_format(self, runner, temp_config_dir, valid_config):
        """Test config list command with JSON output format."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["--format", "json", "config", "list"])

            assert result.exit_code == 0
            
            # Verify JSON output
            output_data = json.loads(result.output)
            assert "canvas" in output_data
            assert output_data["canvas"]["name"] == "Test University"

    def test_config_list_yaml_format(self, runner, temp_config_dir, valid_config):
        """Test config list command with YAML output format."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["--format", "yaml", "config", "list"])

            assert result.exit_code == 0
            
            # Verify YAML output
            output_data = yaml.safe_load(result.output)
            assert "canvas" in output_data
            assert output_data["canvas"]["name"] == "Test University"

    def test_config_list_table_format(self, runner, temp_config_dir, valid_config):
        """Test config list command with table output format (default)."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["config", "list"])

            assert result.exit_code == 0
            assert "Test University" in result.output
            assert "https://test.instructure.com" in result.output


class TestCredentialManagement:
    """Test credential storage and retrieval workflows."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    def test_credential_storage_and_retrieval(self, temp_config_dir):
        """Test storing and retrieving credentials."""
        from easel.config.credentials import CredentialManager

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            cred_manager = CredentialManager()
            
            # Store credential
            cred_manager.store_token("test_instance", "test_token_123")
            
            # Verify storage
            assert cred_manager.has_credentials("test_instance")
            assert "test_instance" in cred_manager.list_stored_instances()
            
            # Retrieve credential
            token = cred_manager.get_token("test_instance")
            assert token == "test_token_123"

    def test_credential_removal(self, temp_config_dir):
        """Test removing stored credentials."""
        from easel.config.credentials import CredentialManager

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            cred_manager = CredentialManager()
            
            # Store and then remove credential
            cred_manager.store_token("test_instance", "test_token_123")
            assert cred_manager.has_credentials("test_instance")
            
            removed = cred_manager.remove_token("test_instance")
            assert removed is True
            assert not cred_manager.has_credentials("test_instance")

    def test_environment_variable_override(self, temp_config_dir):
        """Test credential override via environment variable."""
        from easel.config.credentials import CredentialManager

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            cred_manager = CredentialManager()
            
            # Test environment variable retrieval
            with patch.dict(os.environ, {"CANVAS_API_TOKEN": "env_token_123"}):
                token = cred_manager.get_token_from_env()
                assert token == "env_token_123"


class TestErrorHandling:
    """Test error handling in various workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_missing_config_file_error(self, runner):
        """Test handling of missing configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_config_dir = Path(temp_dir) / ".easel"
            
            with patch("easel.config.paths.get_config_dir", return_value=empty_config_dir):
                result = runner.invoke(cli, ["config", "list"])
                
                assert result.exit_code == 1
                assert "No configuration found" in result.output

    def test_corrupted_config_file_error(self, runner):
        """Test handling of corrupted configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            
            # Create corrupted config file
            config_file = config_dir / "config.yaml"
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: {")
            
            with patch("easel.config.paths.get_config_dir", return_value=config_dir):
                result = runner.invoke(cli, ["config", "list"])
                
                assert result.exit_code == 1
                assert "Configuration file is invalid" in result.output

    def test_permission_error_handling(self, runner):
        """Test handling of permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            
            # Create config file with restrictive permissions
            config_file = config_dir / "config.yaml"
            config_file.touch()
            config_file.chmod(0o000)  # No permissions
            
            try:
                with patch("easel.config.paths.get_config_dir", return_value=config_dir):
                    result = runner.invoke(cli, ["config", "list"])
                    
                    # Should handle permission error gracefully
                    assert result.exit_code == 1
            finally:
                # Restore permissions for cleanup
                config_file.chmod(0o644)


class TestVersionCommand:
    """Test version command workflow."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_version_command(self, runner):
        """Test version command output."""
        result = runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "easel" in result.output.lower()

    def test_version_format_options(self, runner):
        """Test version command with different format options."""
        # Test JSON format
        result = runner.invoke(cli, ["--format", "json", "--version"])
        assert result.exit_code == 0
        
        # Should be valid JSON
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Version output should be valid JSON when format=json")


class TestVerboseOutput:
    """Test verbose output workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory.""" 
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    def test_verbose_output_enabled(self, runner, temp_config_dir):
        """Test verbose output provides additional information."""
        # Create minimal config
        config = EaselConfig(
            canvas=CanvasInstance(
                name="Test University",
                base_url="https://test.instructure.com", 
                api_token="test_token",
            )
        )

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config.model_dump(), f)

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            # Test without verbose
            result_normal = runner.invoke(cli, ["config", "list"])
            
            # Test with verbose
            result_verbose = runner.invoke(cli, ["--verbose", "config", "list"])
            
            assert result_normal.exit_code == 0
            assert result_verbose.exit_code == 0
            
            # Verbose should provide more detailed output
            assert len(result_verbose.output) >= len(result_normal.output)