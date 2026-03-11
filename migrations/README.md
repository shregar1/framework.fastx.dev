# Database Migrations

This directory contains Alembic database migration scripts for FastMVC.

## Overview

Alembic is used to manage database schema changes in a version-controlled,
reversible manner. Each migration file represents a set of changes to the
database schema.

## Directory Structure

```
migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migration files
├── versions/           # Migration script files
│   └── *.py            # Individual migration scripts
└── README.md           # This file
```

## Usage

### Generate a New Migration

After modifying models, generate a migration:

```bash
# Auto-generate from model changes
fastmvc migrate generate "add_product_table"

# Or using alembic directly
alembic revision --autogenerate -m "add_product_table"
```

### Apply Migrations

```bash
# Upgrade to latest
fastmvc migrate upgrade

# Or using alembic directly
alembic upgrade head
```

### Rollback Migrations

```bash
# Rollback one step
fastmvc migrate downgrade

# Or using alembic directly
alembic downgrade -1
```

### View Migration Status

```bash
# Show current revision
fastmvc migrate status

# Or using alembic
alembic current
alembic history
```

## Best Practices

1. **Review auto-generated migrations** - Always check the generated SQL
2. **Test migrations** - Run on a copy of production data first
3. **Keep migrations small** - One logical change per migration
4. **Never edit applied migrations** - Create new migrations for fixes
5. **Include both upgrade and downgrade** - Ensure reversibility

## Configuration

Database connection is configured via environment variables:

```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=fastmvc
DATABASE_USER=postgres
DATABASE_PASSWORD=secret
```

## Troubleshooting

### Migration conflicts

If two developers create migrations simultaneously:

```bash
# Merge migrations
alembic merge heads -m "merge migrations"
```

### Reset migrations (development only)

```bash
# Drop all tables and start fresh
alembic downgrade base
alembic upgrade head
```

