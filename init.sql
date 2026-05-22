-- OrgLens DB initialization
-- Tables are created by SQLAlchemy on startup,
-- this file handles extensions and DB-level config.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- fast LIKE/ILIKE on text columns

-- Useful for full-text search on message content later
ALTER DATABASE orglens SET default_text_search_config = 'english';