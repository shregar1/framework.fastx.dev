# CI/CD with GitHub Actions

FastMVC projects come with pre-configured GitHub Actions workflows for continuous integration and deployment.

## Included Workflows

### 1. CI/CD Workflow (`ci.yml`)

Runs on every push to `main`/`develop` branches and pull requests.

**Jobs:**
- **Test** - Run tests across Python 3.10, 3.11, 3.12
- **Lint** - Code quality checks with Ruff and MyPy
- **Security** - Bandit security scan and dependency vulnerability check
- **Build Docker** - Build and push Docker image to GitHub Container Registry

**Services:**
- PostgreSQL 16 (for database tests)
- Redis 7 (for cache tests)

### 2. PR Checks Workflow (`pr-check.yml`)

Runs on pull requests to validate changes before merging.

**Jobs:**
- **PR Metadata** - Validates PR title format (conventional commits)
- **Fast Checks** - Quick lint and format checks
- **Test Changed Files** - Run tests for modified files
- **Docker Build Test** - Verify Docker image builds successfully
- **Size Check** - Warn if PR changes more than 1000 lines

### 3. Release Workflow (`release.yml`)

Runs when a version tag is pushed (e.g., `v1.0.0`).

**Jobs:**
- **Create Release** - Generate release notes and create GitHub release
- **Build Release Image** - Build and push production Docker image
- **Deploy** - (Customizable) Deploy to production environment

## Setup Instructions

### 1. Enable GitHub Actions

After pushing your project to GitHub:

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

### 2. Configure Secrets (Optional)

For deployment or external services, add secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add your secrets (e.g., `DEPLOY_KEY`, `API_TOKEN`)

### 3. Customize Workflows

Edit the workflow files in `.github/workflows/` to match your needs:

**Update environment variables:**
```yaml
env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

**Modify test matrix:**
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

**Add deployment step:**
```yaml
- name: Deploy to production
  run: |
    # Add your deployment commands
    ssh user@server "docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:main"
```

## Using the Container Registry

Docker images are automatically published to GitHub Container Registry.

### Pull an Image

```bash
# Pull latest main branch image
docker pull ghcr.io/username/repo:main

# Pull specific version
docker pull ghcr.io/username/repo:v1.0.0

# Pull latest release
docker pull ghcr.io/username/repo:latest
```

### Run the Container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET_KEY=your-secret \
  ghcr.io/username/repo:latest
```

## Status Badges

Add this to your `README.md` to show build status:

```markdown
![CI](https://github.com/username/repo/workflows/CI/CD/badge.svg)
![Release](https://github.com/username/repo/workflows/Release/badge.svg)
```

## Local Testing

Test workflows locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act

# Run CI workflow
act push

# Run PR checks
act pull_request
```

## Troubleshooting

### Docker Login Failed

Ensure GitHub Actions has write permissions:
- Go to **Settings** → **Actions** → **General**
- Enable **Read and write permissions**

### Tests Fail in CI but Pass Locally

Common causes:
- DataI/Redis not running in CI
- Environment variables not set
- Different Python version

Check the workflow logs for specific errors.

### Coverage Not Uploading

Ensure you have the `CODECOV_TOKEN` secret set if using private repositories.

## Best Practices

1. **Protect main branch** - Require PR reviews and passing checks
2. **Use tags for releases** - Push `v*` tags to trigger releases
3. **Monitor security alerts** - Enable Dependabot for dependency updates
4. **Keep workflows fast** - Cache dependencies, parallelize jobs
5. **Test before pushing** - Run `make ci` locally to catch issues early

## Customizing for Other Platforms

### GitLab CI

Convert workflows to `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest
```

### Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
- script: |
    pip install -r requirements.txt
    pytest
  displayName: 'Run tests'
```

### Bitbucket Pipelines

Create `bitbucket-pipelines.yml`:

```yaml
image: python:3.11

pipelines:
  default:
    - step:
        name: Test
        script:
          - pip install -r requirements.txt
          - pytest
```
