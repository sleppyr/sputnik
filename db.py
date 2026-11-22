import asyncpg
from config import DATABASE_URL, FERNET_KEY
from cryptography.fernet import Fernet

_fernet = Fernet(FERNET_KEY.encode())
_pool = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS sub_bots (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    token_enc BYTEA NOT NULL,
    bot_username TEXT,
    bot_name TEXT DEFAULT 'Sputnik Bot', -- Сделали дефолтным
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS captures (
    id BIGSERIAL PRIMARY KEY,
    sub_bot_id BIGINT,
    full_name TEXT,
    archived BOOLEAN DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS owners (
    user_id BIGINT PRIMARY KEY,
    premium_until TIMESTAMPTZ,
    bought_slots INTEGER DEFAULT 0
);
"""

async def init_db():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA)

def get_pool():
    return _pool
