"""
Tests for FastMVC Project Generator module.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from fastmvc_cli.generator import ProjectGenerator


class TestProjectGenerator:
    """Tests for ProjectGenerator class."""

    def test_initialization(self):
        """Test ProjectGenerator initialization."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir="/tmp"
        )
        assert generator.project_name == "test_project"
        assert str(generator.output_dir).endswith("tmp")

    def test_initialization_with_options(self):
        """Test ProjectGenerator initialization with options."""
        generator = ProjectGenerator(
            project_name="myapp",
            output_dir="/tmp",
            init_git=True,
            create_venv=True,
            install_deps=True
        )
        assert generator.project_name == "myapp"
        assert generator.init_git is True
        assert generator.create_venv is True
        assert generator.install_deps is True

    def test_project_path(self):
        """Test project path generation."""
        generator = ProjectGenerator(
            project_name="test_project",
            output_dir="/tmp"
        )
        assert "test_project" in str(generator.project_path)

    def test_template_dirs_exist(self):
        """Test TEMPLATE_DIRS constant exists."""
        assert hasattr(ProjectGenerator, 'TEMPLATE_DIRS')
        assert isinstance(ProjectGenerator.TEMPLATE_DIRS, list)
        assert "abstractions" in ProjectGenerator.TEMPLATE_DIRS
        assert "controllers" in ProjectGenerator.TEMPLATE_DIRS
        assert "services" in ProjectGenerator.TEMPLATE_DIRS

    def test_template_files_exist(self):
        """Test TEMPLATE_FILES constant exists."""
        assert hasattr(ProjectGenerator, 'TEMPLATE_FILES')
        assert isinstance(ProjectGenerator.TEMPLATE_FILES, list)
        assert "app.py" in ProjectGenerator.TEMPLATE_FILES
        assert "requirements.txt" in ProjectGenerator.TEMPLATE_FILES

    def test_exclude_patterns_exist(self):
        """Test EXCLUDE_PATTERNS constant exists."""
        assert hasattr(ProjectGenerator, 'EXCLUDE_PATTERNS')
        assert isinstance(ProjectGenerator.EXCLUDE_PATTERNS, list)
        assert "__pycache__" in ProjectGenerator.EXCLUDE_PATTERNS
        assert "*.pyc" in ProjectGenerator.EXCLUDE_PATTERNS

    def test_has_generate_method(self):
        """Test generator has generate method."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert hasattr(generator, 'generate')
        assert callable(generator.generate)


class TestSanitizeName:
    """Tests for project name sanitization."""

    def test_sanitize_name_with_hyphens(self):
        """Test hyphens are replaced with underscores."""
        generator = ProjectGenerator(
            project_name="my-project-name",
            output_dir="/tmp"
        )
        assert generator.project_name == "my_project_name"

    def test_sanitize_name_with_special_chars(self):
        """Test special characters are removed."""
        generator = ProjectGenerator(
            project_name="my@project!name",
            output_dir="/tmp"
        )
        assert generator.project_name == "myprojectname"

    def test_sanitize_name_starting_with_number(self):
        """Test names starting with numbers get underscore prefix."""
        generator = ProjectGenerator(
            project_name="123project",
            output_dir="/tmp"
        )
        assert generator.project_name == "_123project"

    def test_sanitize_name_empty_becomes_default(self):
        """Test empty name becomes default."""
        generator = ProjectGenerator(
            project_name="@#$%",
            output_dir="/tmp"
        )
        assert generator.project_name == "fastmvc_project"

    def test_sanitize_name_alphanumeric(self):
        """Test alphanumeric names are preserved."""
        generator = ProjectGenerator(
            project_name="my_project_123",
            output_dir="/tmp"
        )
        assert generator.project_name == "my_project_123"


class TestShouldExclude:
    """Tests for path exclusion logic."""

    def test_exclude_pycache(self):
        """Test __pycache__ is excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path("__pycache__")) is True

    def test_exclude_pyc_files(self):
        """Test .pyc files are excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path("module.pyc")) is True

    def test_exclude_git(self):
        """Test .git is excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path(".git")) is True

    def test_exclude_env(self):
        """Test .env is excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path(".env")) is True

    def test_exclude_htmlcov(self):
        """Test htmlcov is excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path("htmlcov")) is True

    def test_include_normal_files(self):
        """Test normal files are not excluded."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator._should_exclude(Path("app.py")) is False
        assert generator._should_exclude(Path("models")) is False


class TestGetTemplatePath:
    """Tests for template path resolution."""

    def test_template_path_is_resolved(self):
        """Test template path is resolved."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert generator.template_path is not None
        assert isinstance(generator.template_path, Path)


class TestGenerate:
    """Tests for project generation."""

    @patch('fastmvc_cli.generator.click')
    def test_generate_raises_on_existing_directory(self, mock_click):
        """Test generate raises error if directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the project directory
            project_path = Path(tmpdir) / "existing_project"
            project_path.mkdir()

            generator = ProjectGenerator(
                project_name="existing_project",
                output_dir=tmpdir
            )

            with pytest.raises(FileExistsError):
                generator.generate()

    @patch('fastmvc_cli.generator.click')
    def test_step_outputs_message(self, mock_click):
        """Test _step method outputs message."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        generator._step("Test message")
        mock_click.secho.assert_called()


class TestCopyTemplate:
    """Tests for template copying."""

    @patch('shutil.copy2')
    @patch('fastmvc_cli.generator.ProjectGenerator._copy_directory')
    def test_copy_template_calls_copy(self, mock_copy_dir, mock_copy2):
        """Test _copy_template copies files and directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test_project",
                output_dir=tmpdir
            )
            # Create project path
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._copy_template()


class TestCopyDirectory:
    """Tests for directory copying."""

    def test_copy_directory_excludes_pycache(self):
        """Test _copy_directory skips excluded paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir
            )

            # Create source with __pycache__
            src = Path(tmpdir) / "source"
            src.mkdir()
            pycache = src / "__pycache__"
            pycache.mkdir()

            dst = Path(tmpdir) / "dest"

            generator._copy_directory(src, dst)

            # __pycache__ should not be copied
            assert not (dst / "__pycache__").exists()


class TestCreateEnvExample:
    """Tests for .env.example creation."""

    def test_create_env_example_creates_file(self):
        """Test _create_env_example creates the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._create_env_example()

            env_file = generator.project_path / ".env.example"
            assert env_file.exists()


class TestCreateGitignore:
    """Tests for .gitignore creation."""

    def test_create_gitignore_creates_file(self):
        """Test _create_gitignore creates the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._create_gitignore()

            gitignore = generator.project_path / ".gitignore"
            assert gitignore.exists()


class TestCreateReadme:
    """Tests for README creation."""

    def test_create_readme_creates_file(self):
        """Test _create_readme creates the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._create_readme()

            readme = generator.project_path / "README.md"
            assert readme.exists()

    def test_create_readme_contains_project_name(self):
        """Test README contains project name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="my_awesome_api",
                output_dir=tmpdir
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._create_readme()

            readme = generator.project_path / "README.md"
            content = readme.read_text()
            assert "my_awesome_api" in content


class TestCustomizeConfigs:
    """Tests for configuration customization."""

    def test_customize_configs_method_exists(self):
        """Test _customize_configs method exists."""
        generator = ProjectGenerator(
            project_name="test",
            output_dir="/tmp"
        )
        assert hasattr(generator, '_customize_configs')
        assert callable(generator._customize_configs)


class TestInitGit:
    """Tests for git initialization."""

    @patch('subprocess.run')
    def test_init_git_calls_git_init(self, mock_run):
        """Test _init_git calls git init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir,
                init_git=True
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._init_git()

            # Check git init was called
            mock_run.assert_called()


class TestCreateVenv:
    """Tests for virtual environment creation."""

    @patch('subprocess.run')
    def test_create_venv_calls_python_venv(self, mock_run):
        """Test _create_venv calls python -m venv."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir,
                create_venv=True
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            generator._create_venv()

            mock_run.assert_called()


class TestInstallDeps:
    """Tests for dependency installation."""

    @patch('subprocess.run')
    def test_install_deps_calls_pip(self, mock_run):
        """Test _install_deps calls pip install."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(
                project_name="test",
                output_dir=tmpdir,
                install_deps=True
            )
            generator.project_path.mkdir(parents=True, exist_ok=True)
            # Create requirements.txt
            (generator.project_path / "requirements.txt").write_text("fastapi")
            generator._install_deps()

            mock_run.assert_called()
