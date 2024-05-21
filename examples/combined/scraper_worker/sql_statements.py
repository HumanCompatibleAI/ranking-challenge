POSTGRES_CREATE_TABLE_SCRAPER_DATA = """
CREATE TABLE IF NOT EXISTS {table_name} (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  post_id TEXT NOT NULL UNIQUE,
  source_id TEXT,
  task_id TEXT,
  post_blob JSONB
);
"""

POSTGRES_CREATE_INDEXES_SCRAPER_DATA = """
CREATE INDEX IF NOT EXISTS idx_created_at ON {table_name}(created_at);
CREATE INDEX IF NOT EXISTS idx_post_id ON {table_name}(post_id);
CREATE INDEX IF NOT EXISTS idx_source_id ON {table_name}(source_id);
CREATE INDEX IF NOT EXISTS idx_task_id ON {table_name}(task_id);
"""

POSTGRES_CREATE_TABLE_SCRAPER_ERR = """
CREATE TABLE IF NOT EXISTS {table_name} (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  source_id TEXT,
  task_id TEXT,
  message TEXT
);
"""

POSTGRES_CREATE_INDEXES_SCRAPER_ERR = """
CREATE INDEX IF NOT EXISTS idx_created_at ON {table_name}(created_at);
CREATE INDEX IF NOT EXISTS idx_source_id ON {table_name}(source_id);
CREATE INDEX IF NOT EXISTS idx_task_id ON {table_name}(task_id);
"""
