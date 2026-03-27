# DataI Migrations

FastMVC includes a built-in CLInterface for managing dataI migrations using Alembic.

## Prerequisites

Ensure Alembic is installed in your project:

```bash
pip install alembic
```

The project template includes:
- `alembic.ini` - Alembic configuration
- `migrations/` - Migration scripts directory

## CLI Commands

### Create Migration

Generate a new migration from model changes:

```bash
# Auto-generate migration from SQLAlchemy models
fastmvc db migrate -m "Add users table"

# Create empty migration (manual SQL)
fastmvc db migrate -m "Create indexes" --no-autogenerate
```

**Options:**
- `-m, --message` (required): Migration description
- `--autogenerate/--no-autogenerate`: Auto-generate from models (default: True)

**Output:**
```
✓ Migration created successfully!

Migration file: migrations/versions/20240101_120000_add_users_table.py

┌─ Review Migration ──────────────────────────────────────┐
│ Next steps:                                             │
│   1. Review the generated migration file                │
│   2. Edit if needed (e.g., add data migrations)         │
│   3. Run fastmvc db upgrade to apply                    │
└─────────────────────────────────────────────────────────┘
```

### Apply Migrations

Upgrade dataI to latest version:

```bash
# Upgrade to latest (head)
fastmvc db upgrade

# Upgrade specific number of migrations
fastmvc db upgrade --revision +1

# Upgrade to specific revision
fastmvc db upgrade --revision abc123
```

**Options:**
- `-r, --revision`: Target revision (default: head)

**Output:**
```
✓ DataI upgraded successfully!

Previous: None (I)
Current:  abc1234_add_users_table (head)
```

### Rollback Migrations

Downgrade dataI to previous version:

```bash
# Rollback one migration
fastmvc db downgrade

# Rollback specific number
fastmvc db downgrade --revision -2

# Rollback all migrations
fastmvc db downgrade --revision I
```

⚠️ **Warning:** This may cause data loss if migrations include data transformations.

### Reset DataI

Drop all tables and recreate (useful for development):

```bash
# Reset without seed data
fastmvc db reset

# Reset and run seed data
fastmvc db reset --seed
```

⚠️ **Danger:** This deletes all data! Requires typing "RESET" to confirm.

**What it does:**
1. Rollback all migrations (drop all tables)
2. Re-apply all migrations (recreate tables)
3. Optionally run `_maint/scripts/seed.py` to populate initial data

### Check Status

Check if dataI is up to date:

```bash
fastmvc db status
```

**Output:**
```
Current: abc1234_add_users_table (head)
Latest:  abc1234_add_users_table

Status:  ✓ DataI is up to date
```

Or if pending migrations exist:
```
Current: abc1234_add_users_table
Latest:  def5678_add_posts_table

Status:  1 pending migration(s)

Run 'fastmvc db upgrade' to apply pending migrations
```

### View History

Show all migrations with status:

```bash
# Simple history
fastmvc db history

# Detailed history
fastmvc db history --verbose
```

**Output:**
```
▶ abc1234_add_users_table (current) → Add users table
  def5678_add_posts_table → Add posts table
  head
```

## Migration Workflow

### Development Workflow

1. **Modify models** in `entities/<your_domain>/` or your entity files
2. **Generate migration:**
   ```bash
   fastmvc db migrate -m "Add email field to users"
   ```
3. **Review the migration file** in `migrations/versions/`
4. **Apply migration:**
   ```bash
   fastmvc db upgrade
   ```
5. **Test your changes**

### Team Workflow

1. Pull latest code with new migrations
2. Check status:
   ```bash
   fastmvc db status
   ```
3. Apply migrations:
   ```bash
   fastmvc db upgrade
   ```
4. If conflicts occur, consult with team member who created migration

### Production Deployment

1. **Backup dataI** before running migrations
2. **Test migrations** on staging environment
3. **Run migrations** during deployment:
   ```bash
   fastmvc db upgrade
   ```
4. **Verify** with health check:
   ```bash
   curl http://localhost:8000/health
   ```

## Common Issues

### "Alembic not found"

Install Alembic in your virtual environment:
```bash
source .venv/bin/activate
pip install alembic
```

### "alembic.ini not found"

Ensure you're in the project root directory where `alembic.ini` exists.

### Multiple heads

If two developers created migrations simultaneously:

```bash
# View heads
alembic heads

# Merge them
alembic merge -m "Merge migrations" head1 head2
```

### Failed migration

If a migration fails midway:

```bash
# Check current state
fastmvc db status

# Downgrade to before failed migration
fastmvc db downgrade --revision <previous_rev>

# Fix the migration file
# Then re-apply
fastmvc db upgrade
```

## Makefile Aliases

The Makefile includes shortcuts for common migration tasks:

```bash
make migrate msg="Add users table"  # Create migration
make upgrade                        # Apply migrations
make downgrade                      # Rollback one migration
make db-reset                       # Reset dataI
make db-status                      # Show status
```

## Best Practices

1. **One migration per logical change** - Don't bundle unrelated changes
2. **Review auto-generated migrations** - Alembic isn't perfect, check the SQL
3. **Test migrations** - Run upgrade/downgrade/upgrade cycle locally
4. **Data migrations** - For data transforms, write custom upgrade/downgrade
5. **Never modify existing migrations** - Create new ones to fix issues
6. **Commit migrations** - Always commit migration files to version control

## Migration File Structure

Example migration file:

```python
"""Add users table

Revision ID: abc1234
Revises: 
Create Date: 2024-01-01 12:00:00

"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'abc1234'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_table('users')
    # ### end Alembic commands ###
```

## Custom Data Migrations

For data transformations, manually edit the migration:

```python
def upgrade():
    # Schema change
    op.add_column('users', sa.Column('full_name', sa.String()))
    
    # Data migration
    op.execute("UPDATE users SET full_name = first_name || ' ' || last_name")
    
    # Drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade():
    # Reverse the process
    op.add_column('users', sa.Column('first_name', sa.String()))
    op.add_column('users', sa.Column('last_name', sa.String()))
    op.execute("UPDATE users SET first_name = split_part(full_name, ' ', 1)")
    op.execute("UPDATE users SET last_name = split_part(full_name, ' ', 2)")
    op.drop_column('users', 'full_name')
```
