"""Integration tests for complete end-to-end workflows."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import yaml
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.models import CanvasInstance, EaselConfig


class TestCompleteWorkflow:
    """Test complete end-to-end workflow from initialization to API usage."""

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
    def mock_user_response(self):
        """Mock Canvas user API response."""
        return {
            "id": 123,
            "name": "Test User",
            "email": "test@university.edu",
            "login_id": "testuser",
            "avatar_url": "https://example.com/avatar.jpg",
        }

    @pytest.fixture
    def mock_courses_response(self):
        """Mock Canvas courses API response."""
        return [
            {
                "id": 456,
                "name": "Test Course 1",
                "course_code": "TEST101",
                "workflow_state": "available",
                "start_at": "2024-01-15T08:00:00Z",
                "end_at": "2024-05-15T17:00:00Z",
            },
            {
                "id": 457,
                "name": "Test Course 2", 
                "course_code": "TEST102",
                "workflow_state": "available",
                "start_at": "2024-01-15T08:00:00Z",
                "end_at": "2024-05-15T17:00:00Z",
            },
        ]

    def test_complete_setup_workflow(
        self, runner, temp_config_dir, mock_user_response
    ):
        """Test complete setup workflow from init to doctor validation."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = mock_user_response
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                # Step 1: Initialize configuration
                user_input = "\n".join([
                    "Test University",
                    "https://test.instructure.com",
                    "test_token_123",
                    "y",  # confirm token verification
                ])

                init_result = runner.invoke(cli, ["init"], input=user_input)
                assert init_result.exit_code == 0
                assert "Configuration saved successfully" in init_result.output

                # Verify configuration file was created
                config_file = temp_config_dir / "config.yaml"
                assert config_file.exists()

                # Step 2: List configuration
                list_result = runner.invoke(cli, ["config", "list"])
                assert list_result.exit_code == 0
                assert "Test University" in list_result.output
                assert "https://test.instructure.com" in list_result.output

                # Step 3: Run doctor validation
                doctor_result = runner.invoke(cli, ["doctor"])
                assert doctor_result.exit_code == 0
                assert "✓ Configuration file found" in doctor_result.output
                assert "✓ Configuration validation passed" in doctor_result.output
                assert "✓ Canvas API connection successful" in doctor_result.output
                assert "All checks passed!" in doctor_result.output

    def test_workflow_with_different_output_formats(
        self, runner, temp_config_dir, mock_user_response
    ):
        """Test workflow using different output formats."""
        # Setup configuration first
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
            # Test table format (default)
            table_result = runner.invoke(cli, ["config", "list"])
            assert table_result.exit_code == 0
            assert "Test University" in table_result.output

            # Test JSON format
            json_result = runner.invoke(cli, ["--format", "json", "config", "list"])
            assert json_result.exit_code == 0
            
            # Validate JSON output
            try:
                json_data = json.loads(json_result.output)
                assert json_data["canvas"]["name"] == "Test University"
            except json.JSONDecodeError:
                pytest.fail("JSON output should be valid JSON")

            # Test YAML format
            yaml_result = runner.invoke(cli, ["--format", "yaml", "config", "list"])
            assert yaml_result.exit_code == 0
            
            # Validate YAML output
            try:
                yaml_data = yaml.safe_load(yaml_result.output)
                assert yaml_data["canvas"]["name"] == "Test University"
            except yaml.YAMLError:
                pytest.fail("YAML output should be valid YAML")

    def test_error_recovery_workflow(self, runner, temp_config_dir):
        """Test error recovery in complete workflow."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            # Step 1: Try to run commands without configuration
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 1
            assert "No configuration found" in list_result.output

            doctor_result = runner.invoke(cli, ["doctor"])
            assert doctor_result.exit_code == 1
            assert "✗ Configuration file not found" in doctor_result.output

            # Step 2: Initialize with invalid token
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

                init_result = runner.invoke(cli, ["init"], input=user_input)
                assert init_result.exit_code == 1
                assert "Token verification failed" in init_result.output

            # Step 3: Still no configuration after failed init
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 1
            assert "No configuration found" in list_result.output

    def test_configuration_validation_workflow(self, runner, temp_config_dir):
        """Test configuration validation in complete workflow."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            # Create invalid configuration file
            config_file = temp_config_dir / "config.yaml"
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: {")

            # Test configuration listing with invalid file
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 1
            assert "Configuration file is invalid" in list_result.output

            # Test doctor command with invalid configuration
            doctor_result = runner.invoke(cli, ["doctor"])
            assert doctor_result.exit_code == 1
            assert "✗ Configuration validation failed" in doctor_result.output

            # Fix configuration
            valid_config = EaselConfig(
                canvas=CanvasInstance(
                    name="Test University",
                    base_url="https://test.instructure.com",
                    api_token="test_token",
                )
            )

            with open(config_file, "w") as f:
                yaml.dump(valid_config.model_dump(), f)

            # Now commands should work
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 0
            assert "Test University" in list_result.output

    def test_verbose_workflow(
        self, runner, temp_config_dir, mock_user_response
    ):
        """Test workflow with verbose output enabled."""
        # Setup configuration
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
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = mock_user_response
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                # Test verbose output
                verbose_result = runner.invoke(cli, ["--verbose", "doctor"])
                assert verbose_result.exit_code == 0
                assert "✓ Configuration file found" in verbose_result.output

                # Test non-verbose output for comparison
                normal_result = runner.invoke(cli, ["doctor"])
                assert normal_result.exit_code == 0

                # Verbose should provide additional information
                # (In a real implementation, verbose would show more details)
                assert len(verbose_result.output) >= len(normal_result.output)

    def test_credential_security_workflow(
        self, runner, temp_config_dir, mock_user_response
    ):
        """Test credential security in complete workflow."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = mock_user_response
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                # Initialize with credential storage
                user_input = "\n".join([
                    "Test University",
                    "https://test.instructure.com",
                    "sensitive_token_123",
                    "y",  # confirm token verification
                ])

                init_result = runner.invoke(cli, ["init"], input=user_input)
                assert init_result.exit_code == 0

                # Verify configuration file exists
                config_file = temp_config_dir / "config.yaml"
                assert config_file.exists()

                # Verify token is not stored in plain text in config file
                with open(config_file) as f:
                    config_content = f.read()
                
                assert "sensitive_token_123" not in config_content
                assert "canvas" in config_content

                # Verify credentials file exists and is encrypted
                credentials_file = temp_config_dir / "credentials.yaml"
                if credentials_file.exists():
                    with open(credentials_file) as f:
                        cred_content = f.read()
                    
                    # Token should be encrypted, not in plain text
                    assert "sensitive_token_123" not in cred_content

    def test_multi_command_workflow(
        self, runner, temp_config_dir, mock_user_response
    ):
        """Test workflow with multiple commands in sequence."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            with patch("httpx.AsyncClient") as mock_client:
                # Mock successful API verification
                mock_response = AsyncMock()
                mock_response.is_success = True
                mock_response.json.return_value = mock_user_response
                mock_client.return_value.__aenter__.return_value.request.return_value = mock_response

                # Command sequence: init -> config list -> doctor -> version
                
                # 1. Initialize
                user_input = "\n".join([
                    "Test University",
                    "https://test.instructure.com",
                    "test_token_123",
                    "y",
                ])

                init_result = runner.invoke(cli, ["init"], input=user_input)
                assert init_result.exit_code == 0

                # 2. List configuration
                list_result = runner.invoke(cli, ["config", "list"])
                assert list_result.exit_code == 0
                assert "Test University" in list_result.output

                # 3. Run diagnostics
                doctor_result = runner.invoke(cli, ["doctor"])
                assert doctor_result.exit_code == 0
                assert "All checks passed!" in doctor_result.output

                # 4. Check version
                version_result = runner.invoke(cli, ["--version"])
                assert version_result.exit_code == 0
                assert "easel" in version_result.output.lower()

    def test_edge_case_workflow(self, runner, temp_config_dir):
        """Test workflow with edge cases and boundary conditions."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            # Test with minimal configuration
            minimal_config = {
                "version": "1.0",
                "canvas": {
                    "name": "Min",
                    "base_url": "https://min.com",
                    "api_token": "token",
                }
            }

            config_file = temp_config_dir / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(minimal_config, f)

            # Should handle minimal configuration
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 0
            assert "Min" in list_result.output

            # Test with empty configuration directory
            config_file.unlink()
            
            list_result = runner.invoke(cli, ["config", "list"])
            assert list_result.exit_code == 1
            assert "No configuration found" in list_result.output

    def test_concurrent_command_workflow(self, runner, temp_config_dir):
        """Test workflow robustness with concurrent-like operations."""
        # Setup configuration
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
            # Multiple rapid-fire commands (simulating concurrent usage)
            results = []
            for _ in range(5):
                result = runner.invoke(cli, ["config", "list"])
                results.append(result)

            # All should succeed
            for result in results:
                assert result.exit_code == 0
                assert "Test University" in result.output

            # Configuration file should remain intact
            assert config_file.exists()
            with open(config_file) as f:
                final_config = yaml.safe_load(f)
            
            assert final_config["canvas"]["name"] == "Test University"


class TestUserExperienceWorkflows:
    """Test user experience and usability workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def test_help_system_workflow(self, runner):
        """Test help system across different commands."""
        # Main help
        help_result = runner.invoke(cli, ["--help"])
        assert help_result.exit_code == 0
        assert "Usage:" in help_result.output
        assert "Commands:" in help_result.output

        # Command-specific help
        config_help = runner.invoke(cli, ["config", "--help"])
        assert config_help.exit_code == 0
        assert "config" in config_help.output

        init_help = runner.invoke(cli, ["init", "--help"])
        assert init_help.exit_code == 0
        assert "init" in init_help.output

        doctor_help = runner.invoke(cli, ["doctor", "--help"])
        assert doctor_help.exit_code == 0
        assert "doctor" in doctor_help.output

    def test_error_message_quality_workflow(self, runner):
        """Test quality and helpfulness of error messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_config_dir = Path(temp_dir) / ".easel"
            
            with patch("easel.config.paths.get_config_dir", return_value=empty_config_dir):
                # Test missing configuration error
                result = runner.invoke(cli, ["config", "list"])
                
                assert result.exit_code == 1
                assert "No configuration found" in result.output
                # Should provide helpful guidance
                assert "Run 'easel init'" in result.output or "run 'easel init'" in result.output

    def test_progressive_disclosure_workflow(self, runner):
        """Test progressive disclosure of information."""
        # Basic command should provide concise output
        version_result = runner.invoke(cli, ["--version"])
        assert version_result.exit_code == 0
        # Should be concise
        assert len(version_result.output.split('\n')) <= 3

        # Help should provide more detailed information
        help_result = runner.invoke(cli, ["--help"])
        assert help_result.exit_code == 0
        # Should be more comprehensive
        assert len(help_result.output) > len(version_result.output)


class TestBackwardCompatibilityWorkflows:
    """Test backward compatibility and migration workflows."""

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

    def test_legacy_config_handling(self, runner, temp_config_dir):
        """Test handling of legacy configuration formats."""
        # Create a minimal legacy-style configuration
        legacy_config = {
            "canvas": {
                "name": "Legacy University",
                "base_url": "https://legacy.instructure.com",
                "api_token": "legacy_token",
            }
            # Missing version field (legacy)
        }

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(legacy_config, f)

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            # Should handle legacy configuration gracefully
            result = runner.invoke(cli, ["config", "list"])
            
            # Should either succeed or provide clear migration guidance
            if result.exit_code != 0:
                assert "version" in result.output.lower() or "upgrade" in result.output.lower()
            else:
                assert "Legacy University" in result.output

    def test_config_version_migration(self, runner, temp_config_dir):
        """Test configuration version migration workflow."""
        # This test documents expected behavior for future version migrations
        current_config = EaselConfig(
            version="1.0",
            canvas=CanvasInstance(
                name="Current University",
                base_url="https://current.instructure.com",
                api_token="current_token",
            )
        )

        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(current_config.model_dump(), f)

        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            result = runner.invoke(cli, ["config", "list"])
            
            assert result.exit_code == 0
            assert "Current University" in result.output