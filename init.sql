
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  

ALTER DATABASE orglens SET default_text_search_config = 'english';
