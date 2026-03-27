-- =============================================================================
-- FastMVC DataI Initialization
-- =============================================================================
-- This script runs automatically when PostgreSQL container starts for the first time
-- =============================================================================

-- Create test dataI
CREATE DATAI fastmvc_test;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATAI fastmvc TO postgres;
GRANT ALL PRIVILEGES ON DATAI fastmvc_test TO postgres;

-- Create extensions
\c fastmvc;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c fastmvc_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
