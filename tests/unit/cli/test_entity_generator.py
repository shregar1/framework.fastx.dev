"""
Tests for FastMVC Entity Generator module.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from fastmvc_cli.entity_generator import EntityGenerator


class TestEntityGenerator:
    """Tests for EntityGenerator class."""

    def test_initialization(self):
        """Test EntityGenerator initialization."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator.entity_name == "Product"
        assert "project" in str(generator.project_path)

    def test_initialization_with_tests_disabled(self):
        """Test EntityGenerator with tests disabled."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project",
            with_tests=False
        )
        assert generator.with_tests is False

    def test_entity_lower_property(self):
        """Test entity_lower property."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator.entity_lower == "product"

    def test_entity_snake_property(self):
        """Test entity_snake property for camelcase."""
        generator = EntityGenerator(
            entity_name="ProductCategory",
            project_path="/tmp/project"
        )
        assert generator.entity_snake == "product_category"

    def test_has_generate_method(self):
        """Test EntityGenerator has generate method."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert hasattr(generator, 'generate')
        assert callable(generator.generate)


class TestToSnakeCase:
    """Tests for snake_case conversion."""

    def test_simple_camelcase(self):
        """Test simple CamelCase conversion."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator._to_snake_case("Product") == "product"

    def test_multi_word_camelcase(self):
        """Test multi-word CamelCase conversion."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator._to_snake_case("ProductCategory") == "product_category"
        assert generator._to_snake_case("OrderItem") == "order_item"
        assert generator._to_snake_case("UserProfile") == "user_profile"

    def test_acronym_camelcase(self):
        """Test acronym in CamelCase."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        result = generator._to_snake_case("APIResponse")
        assert "api" in result.lower()


class TestToCamelCase:
    """Tests for CamelCase conversion."""

    def test_simple_snake_case(self):
        """Test simple snake_case conversion."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator._to_camel_case("product") == "Product"

    def test_multi_word_snake_case(self):
        """Test multi-word snake_case conversion."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert generator._to_camel_case("product_category") == "ProductCategory"
        assert generator._to_camel_case("order_item") == "OrderItem"


class TestGenerateModel:
    """Tests for model generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_model_creates_file(self, mock_click):
        """Test _generate_model creates model file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create models directory
            models_dir = Path(tmpdir) / "models"
            models_dir.mkdir()
            (models_dir / "__init__.py").write_text("")

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_model()

            model_file = models_dir / "product.py"
            assert model_file.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_model_contains_class(self, mock_click):
        """Test generated model contains class definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            models_dir = Path(tmpdir) / "models"
            models_dir.mkdir()
            (models_dir / "__init__.py").write_text("")

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_model()

            model_file = models_dir / "product.py"
            content = model_file.read_text()
            assert "class Product" in content
            assert "__tablename__" in content


class TestGenerateRepository:
    """Tests for repository generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_repository_creates_file(self, mock_click):
        """Test _generate_repository creates repository file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "repositories"
            repos_dir.mkdir()
            (repos_dir / "__init__.py").write_text("")

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_repository()

            repo_file = repos_dir / "product.py"
            assert repo_file.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_repository_contains_class(self, mock_click):
        """Test generated repository contains class definition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "repositories"
            repos_dir.mkdir()
            (repos_dir / "__init__.py").write_text("")

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_repository()

            repo_file = repos_dir / "product.py"
            content = repo_file.read_text()
            assert "ProductRepository" in content
            assert "IRepository" in content


class TestGenerateDTOs:
    """Tests for DTO generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_dtos_creates_directory(self, mock_click):
        """Test _generate_dtos creates DTO directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dtos_dir = Path(tmpdir) / "dtos" / "requests"
            dtos_dir.mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_dtos()

            product_dto_dir = dtos_dir / "product"
            assert product_dto_dir.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_dtos_creates_create_dto(self, mock_click):
        """Test _generate_dtos creates create DTO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dtos_dir = Path(tmpdir) / "dtos" / "requests"
            dtos_dir.mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_dtos()

            create_dto = dtos_dir / "product" / "create.py"
            assert create_dto.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_dtos_creates_update_dto(self, mock_click):
        """Test _generate_dtos creates update DTO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dtos_dir = Path(tmpdir) / "dtos" / "requests"
            dtos_dir.mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_dtos()

            update_dto = dtos_dir / "product" / "update.py"
            assert update_dto.exists()


class TestGenerateService:
    """Tests for service generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_service_creates_directory(self, mock_click):
        """Test _generate_service creates service directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir) / "services"
            services_dir.mkdir()

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_service()

            product_service_dir = services_dir / "product"
            assert product_service_dir.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_service_creates_abstraction(self, mock_click):
        """Test _generate_service creates abstraction file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir) / "services"
            services_dir.mkdir()

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_service()

            abstraction = services_dir / "product" / "abstraction.py"
            assert abstraction.exists()

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_service_creates_crud(self, mock_click):
        """Test _generate_service creates CRUD file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            services_dir = Path(tmpdir) / "services"
            services_dir.mkdir()

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_service()

            crud = services_dir / "product" / "crud.py"
            assert crud.exists()


class TestGenerateController:
    """Tests for controller generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_controller_creates_directory(self, mock_click):
        """Test _generate_controller creates controller directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            controllers_dir = Path(tmpdir) / "controllers"
            controllers_dir.mkdir()

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_controller()

            product_controller_dir = controllers_dir / "product"
            assert product_controller_dir.exists()


class TestGenerateDependencies:
    """Tests for dependency generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_dependencies_creates_repo_dependency(self, mock_click):
        """Test _generate_dependencies creates repository dependency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deps_dir = Path(tmpdir) / "dependencies" / "repositiories"
            deps_dir.mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir
            )
            generator._generate_dependencies()

            repo_dep = deps_dir / "product.py"
            assert repo_dep.exists()


class TestGenerateTests:
    """Tests for test generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_tests_creates_model_test(self, mock_click):
        """Test _generate_tests creates model test file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tests_dir = Path(tmpdir) / "tests" / "unit" / "models"
            tests_dir.mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Product",
                project_path=tmpdir,
                with_tests=True
            )
            generator._generate_tests()

            model_test = tests_dir / "test_product.py"
            assert model_test.exists()


class TestUpdateInitFiles:
    """Tests for __init__.py updates."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_update_init_files_exists(self, mock_click):
        """Test _update_init_files method exists."""
        generator = EntityGenerator(
            entity_name="Product",
            project_path="/tmp/project"
        )
        assert hasattr(generator, '_update_init_files')
        assert callable(generator._update_init_files)


class TestFullGeneration:
    """Tests for full entity generation."""

    @patch('fastmvc_cli.entity_generator.click')
    def test_generate_creates_all_files(self, mock_click):
        """Test generate creates all necessary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            (Path(tmpdir) / "models").mkdir()
            (Path(tmpdir) / "models" / "__init__.py").write_text("")
            (Path(tmpdir) / "repositories").mkdir()
            (Path(tmpdir) / "repositories" / "__init__.py").write_text("")
            (Path(tmpdir) / "services").mkdir()
            (Path(tmpdir) / "controllers").mkdir()
            (Path(tmpdir) / "dtos" / "requests").mkdir(parents=True)
            (Path(tmpdir) / "dependencies" / "repositiories").mkdir(parents=True)
            (Path(tmpdir) / "dependencies" / "services").mkdir(parents=True)
            (Path(tmpdir) / "tests" / "unit" / "models").mkdir(parents=True)
            (Path(tmpdir) / "tests" / "unit" / "repositories").mkdir(parents=True)
            (Path(tmpdir) / "tests" / "unit" / "services").mkdir(parents=True)

            generator = EntityGenerator(
                entity_name="Order",
                project_path=tmpdir,
                with_tests=True
            )
            generator.generate()

            # Check files were created
            assert (Path(tmpdir) / "models" / "order.py").exists()
            assert (Path(tmpdir) / "repositories" / "order.py").exists()
            assert (Path(tmpdir) / "services" / "order").exists()
