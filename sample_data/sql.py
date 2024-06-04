SQLITE_CREATE_TABLE_POSTS = """
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id TEXT,
  session_timestamp TIMESTAMP,
  session_user_id TEXT,
  platform TEXT,
  type TEXT,
  author_name_hash TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  post_blob TEXT
)"""

SQLITE_CREATE_INDEXES_POSTS = """
CREATE INDEX idx_created_at ON posts(created_at);
CREATE INDEX idx_post_id ON posts(post_id);
CREATE INDEX idx_session_user_id ON posts(session_user_id);
"""

POSTGRES_CREATE_TABLE_POSTS = """
CREATE TABLE IF NOT EXISTS posts (
  id SERIAL PRIMARY KEY,
  post_id TEXT,
  session_timestamp TIMESTAMP WITH TIME ZONE,
  session_user_id TEXT,
  platform TEXT,
  type TEXT,
  author_name_hash TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  post_blob JSONB
);
"""

POSTGRES_CREATE_INDEXES_POSTS = """
CREATE INDEX IF NOT EXISTS idx_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_post_id ON posts(post_id);
CREATE INDEX IF NOT EXISTS idx_session_user_id ON posts(session_user_id);
"""
