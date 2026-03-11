"""
Tests for FastMVC CLI module.
"""

from click.testing import CliRunner

from fastmvc_cli.cli import cli, main


class TestCLIMain:
    """Tests for main CLI entry point."""

    def test_main_function_exists(self):
        """Test main function exists."""
        assert callable(main)

    def test_cli_group_exists(self):
        """Test CLI group exists."""
        assert cli is not None


class TestCLIVersion:
    """Tests for version command."""

    def test_version_command(self):
        """Test version command outputs version."""
        runner = CliRunner()
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert 'FastMVC' in result.output or 'fastmvc' in result.output.lower()

    def test_version_option(self):
        """Test --version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0


class TestCLIInfo:
    """Tests for info command."""

    def test_info_command(self):
        """Test info command outputs framework info."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        assert 'FastMVC' in result.output


class TestCLIGenerate:
    """Tests for generate command."""

    def test_generate_help(self):
        """Test generate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '--help'])
        assert result.exit_code == 0
        assert 'project' in result.output.lower() or 'name' in result.output.lower()


class TestCLIAddEntity:
    """Tests for add entity command."""

    def test_add_entity_help(self):
        """Test add entity command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['add', 'entity', '--help'])
        assert result.exit_code == 0


class TestCLIMigrate:
    """Tests for migrate commands."""

    def test_migrate_help(self):
        """Test migrate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', '--help'])
        assert result.exit_code == 0

    def test_migrate_generate_help(self):
        """Test migrate generate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', 'generate', '--help'])
        assert result.exit_code == 0

    def test_migrate_upgrade_help(self):
        """Test migrate upgrade command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', 'upgrade', '--help'])
        assert result.exit_code == 0

    def test_migrate_downgrade_help(self):
        """Test migrate downgrade command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', 'downgrade', '--help'])
        assert result.exit_code == 0

    def test_migrate_status_help(self):
        """Test migrate status command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', 'status', '--help'])
        assert result.exit_code == 0

    def test_migrate_history_help(self):
        """Test migrate history command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['migrate', 'history', '--help'])
        assert result.exit_code == 0
