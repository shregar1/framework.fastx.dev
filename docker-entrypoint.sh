#!/bin/sh
# =============================================================================
# FastMVC Docker Entrypoint
# =============================================================================
# This script handles database migrations and application startup
# =============================================================================

set -e

echo "🚀 FastMVC Startup"
echo "=================="

# =============================================================================
# Wait for dependencies
# =============================================================================

echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h "${POSTGRES_HOST:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}"; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "✅ PostgreSQL is up"

echo "⏳ Waiting for Redis..."
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping | grep -q PONG; do
    echo "Redis is unavailable - sleeping"
    sleep 1
done
echo "✅ Redis is up"

# =============================================================================
# Run migrations (optional, can be disabled)
# =============================================================================

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "📊 Running database migrations..."
    alembic upgrade head
    echo "✅ Migrations complete"
else
    echo "⏭️  Skipping migrations (RUN_MIGRATIONS=false)"
fi

# =============================================================================
# Seed data (optional)
# =============================================================================

if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "🌱 Running seed data..."
    python _maint/scripts/seed.py || echo "⚠️  Seed script failed or not found"
fi

# =============================================================================
# Start application
# =============================================================================

echo "🎯 Starting application..."

# Check if a custom command was provided
if [ $# -gt 0 ]; then
    echo "Running custom command: $@"
    exec "$@"
else
    # Default: run with uvicorn
    echo "Starting Uvicorn server..."
    exec uvicorn app:app \
        --host "${HOST:-0.0.0.0}" \
        --port "${PORT:-8000}" \
        --workers "${WORKERS:-4}" \
        --log-level "${LOG_LEVEL:-info}" \
        --proxy-headers \
        --forwarded-allow-ips "*"
fi
