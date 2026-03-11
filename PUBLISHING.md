# Publishing FastMVC to PyPI

This guide covers publishing FastMVC to the Python Package Index (PyPI).

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens:
   - PyPI: Account Settings → API tokens → Add API token
   - TestPyPI: Same process on test.pypi.org

3. **Install uv (Recommended)**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   Or using pip:
   ```bash
   pip install uv
   ```

## Configuration

### Option 1: Using .pypirc (Traditional)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Secure the file:
```bash
chmod 600 ~/.pypirc
```

### Option 2: Using Environment Variables (Recommended for CI)

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
```

### Option 3: Using keyring (Most Secure)

```bash
uv pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your token when prompted
```

## Build Process

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

### 2. Run Tests

```bash
# Using uv (recommended)
uv run pytest tests/ -v --cov

# Using pip
pytest tests/ -v --cov
```

### 3. Check Code Quality

```bash
# Using uv
uv run ruff check .
uv run ruff format --check .

# Or with tools installed globally
ruff check .
ruff format --check .
```

### 4. Update Version

Update version in `pyproject.toml` and `fastmvc_cli/__init__.py`:

```toml
# pyproject.toml
[project]
version = "1.2.1"  # Increment appropriately
```

```python
# fastmvc_cli/__init__.py
__version__ = "1.2.1"
```

### 5. Update CHANGELOG

Add release notes to `CHANGELOG.md`.

### 6. Build Package

```bash
# Using uv (recommended - much faster!)
uv build

# Using pip
python -m build
```

This creates:
- `dist/pyfastmvc-x.x.x.tar.gz` (source distribution)
- `dist/pyfastmvc-x.x.x-py3-none-any.whl` (wheel)

### 7. Verify Build

```bash
uv pip install twine
twine check dist/*
```

## Publishing

### Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation with uv
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyfastmvc

# Or with pip
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyfastmvc
```

### Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify installation
uv pip install pyfastmvc
fastmvc version
```

## GitHub Actions (CI/CD)

The repository includes `.github/workflows/publish.yml` which uses uv:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.11

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

Configure Trusted Publishing at: https://pypi.org/manage/project/pyfastmvc/settings/publishing/

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

### Pre-release Versions

```
1.0.0a1   # Alpha
1.0.0b1   # Beta
1.0.0rc1  # Release Candidate
1.0.0     # Final Release
```

## Post-Release

1. **Create Git Tag**:
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

2. **Create GitHub Release**:
   - Go to Releases → Draft a new release
   - Select the tag
   - Add release notes from CHANGELOG
   - Attach wheel and tarball from dist/

3. **Announce**:
   - Update documentation
   - Post on social media
   - Update any external references

## Troubleshooting

### "Package already exists"

You cannot overwrite existing versions. Increment the version number.

### "Invalid classifier"

Check classifiers against the [official list](https://pypi.org/classifiers/).

### "README rendering issues"

```bash
# Check README rendering
uv pip install readme-renderer
python -m readme_renderer README.md
```

### "Missing files in distribution"

Check `MANIFEST.in` and `pyproject.toml` package-data settings.

## Quick Reference

```bash
# Full release process with uv
rm -rf build/ dist/ *.egg-info/
uv run pytest tests/ -v
uv build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Production
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```
