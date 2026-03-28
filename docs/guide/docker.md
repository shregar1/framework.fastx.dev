# Docker Compose Stack

FastMVC includes a complete Docker Compose stack with PostgreSQL, Redis, and the FastAPI application.

## Prerequisites

1. **Docker** — [Docker Desktop](https://docs.docker.com/get-docker/) (macOS/Windows) or Docker Engine + Compose v2 on Linux. The daemon must be **running** (`docker info` should succeed).
2. **Secrets** — Compose sets a **development-only** default `JWT_SECRET_KEY` (32+ characters, meets app validation). For any real deployment, set **`JWT_SECRET_KEY`** and **`SECRET_KEY`** in a `.env` file next to `docker-compose.yml` and never commit production values.

## Quick Start

```bash
# From the repository root (fast_mvc/)
docker compose up -d --build

# Legacy Compose v1 alias (if installed)
docker-compose up -d --build

# Or use make
make docker-up
```

This starts:

- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **FastAPI app** (port 8000) with auto-migrations

## Services

### Core Services (Always Started)

| Service | Description | Port | Health Check |
|---------|-------------|------|--------------|
| `postgres` | PostgreSQL 16 database | 5432 | `pg_isready` |
| `redis` | Redis 7 cache | 6379 | `redis-cli ping` |
| `migrations` | Alembic migrations (runs once) | - | Exits on completion |
| `app` | FastAPI application | 8000 | `/health/live` |

### Optional Services (Profiles)

| Service | Profile | Description | Port |
|---------|---------|-------------|------|
| `worker` | `worker`, `full` | Celery background worker | - |
| `scheduler` | `worker`, `full` | Celery beat scheduler | - |
| `nginx` | `nginx`, `full` | Reverse proxy with SSL | 80, 443 |
| `pgadmin` | `dev`, `admin` | PostgreSQL admin GUI | 5050 |
| `redis-insight` | `dev`, `admin` | Redis GUI | 5540 |

## Usage

### Basic Usage

```bash
# Start core services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### With Make Commands

```bash
# Start full stack
make docker-up

# Start with development tools (PgAdmin, Redis Insight)
make docker-up-dev

# Start with all services (workers, nginx)
make docker-up-full

# View logs
make docker-logs
make docker-logs-app  # App only

# DataI operations
make docker-db-shell      # PostgreSQL CLI
make docker-redis-shell   # Redis CLI
make docker-migrate       # Run migrations

# Cleanup
make docker-down          # Stop services
make docker-down-v        # Stop and remove data
make docker-clean         # Full cleanup
```

### Using Profiles

```bash
# Start with development tools
docker-compose --profile dev up -d

# Start with background workers
docker-compose --profile worker up -d

# Start everything
docker-compose --profile full up -d

# Combine profiles
docker-compose --profile dev --profile worker up -d
```

## Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.docker .env
```

Key variables:

```bash
# DataI
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=fastmvc

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key

# App
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
WORKERS=4
```

### Port Configuration

Change ports in `.env`:

```bash
APP_PORT=8080           # FastAPI app
POSTGRES_PORT=5433      # PostgreSQL
REDIS_PORT=6380         # Redis
PGADMIN_PORT=5050       # PgAdmin
```

## DataI Migrations

Migrations run automatically when the stack starts. To run manually:

```bash
# Using make
make docker-migrate

# Using docker-compose
docker-compose run --rm migrations

# Or with alembic directly
docker-compose exec app alembic upgrade head
```

### Migration Workflow

1. **Modify models** in your code
2. **Generate migration** (outside Docker):

   ```bash
   fastmvc db migrate -m "Add users table"
   ```

3. **Rebuild and restart**:

   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Development Tools

### PgAdmin (PostgreSQL GUI)

```bash
docker-compose --profile dev up -d pgadmin
```

Access at http://localhost:5050

- Email: `admin@example.com` (from `.env`)
- Password: `admin` (from `.env`)

### Redis Insight

```bash
docker-compose --profile dev up -d redis-insight
```

Access at http://localhost:5540

## Production Deployment

### Using Nginx

```bash
docker-compose --profile nginx up -d
```

Place SSL certificates in `_maint/nginx/ssl/`:
_maint/nginx/
├── nginx.conf
└── ssl/
    ├── cert.pem
    └── key.pem

### Environment for Production

```bash
# .env
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
WORKERS=4

# Strong secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# PostgreSQL
POSTGRES_PASSWORD=$(openssl rand -hex 16)
```

### Docker Swarm

```bash
# Deploy to swarm
docker stack deploy -c docker-compose.yml fastmvc

# Check status
docker stack ps fastmvc
docker service ls
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Use different port in .env
APP_PORT=8080
```

### DataI Connection Failed

```bash
# Check postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Reset everything
docker-compose down -v
docker-compose up -d
```

### Migrations Not Running

```bash
# Run migrations manually
docker-compose run --rm migrations

# Check migration status
docker-compose exec app alembic current
docker-compose exec app alembic history
```

### Permission Denied (Linux)

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or use Docker user
# In docker-compose.yml, add to app service:
# user: "${UID}:${GID}"
```

## Data Persistence

Data is stored in Docker volumes:

```bash
# List volumes
docker volume ls

# Backup database
docker-compose exec postgres pg_dump -U postgres fastmvc > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres

# Remove all data (⚠️ destructive)
docker-compose down -v
```

## Health Checks

All services include health checks:

```bash
# Check all services
docker-compose ps

# Check app health
curl http://localhost:8000/health

# Check individual service
docker-compose exec app curl -f http://localhost:8000/health/live
docker-compose exec postgres pg_isready -U postgres
docker-compose exec redis redis-cli ping
```

## Scaling

```bash
# Scale workers
docker-compose up -d --scale worker=3

# Or in docker-compose.yml
deploy:
  replicas: 3
```

## Building Custom Images

```bash
# Build with custom tag
docker-compose build --pull --no-cache

# Push to registry
docker-compose push
```

## Complete Example

```bash
# 1. Clone and setup
git clone <your-repo>
cd <project>
cp .env.docker .env
# Edit .env with your settings

# 2. Start with all dev tools
make docker-up-dev

# 3. Check everything is running
make docker-ps

# 4. View logs
make docker-logs

# 5. Access services
open http://localhost:8000/docs      # API docs
open http://localhost:5050           # PgAdmin
open http://localhost:5540           # Redis Insight

# 6. Run migrations (if needed)
make docker-migrate

# 7. Create test data
docker-compose exec app python _maint/scripts/seed.py

# 8. When done
make docker-down
```
