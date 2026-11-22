# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN     = os.getenv("BOT_TOKEN", "")
FERNET_KEY    = os.getenv("FERNET_KEY", "")
DATABASE_URL  = os.getenv("DATABASE_URL", "")

PG_POOL_MIN = 1
PG_POOL_MAX = 8

ADMIN_IDS         = {8517129681}
FREE_BOTS         = 3
SLOT_PRICE_STARS  = 79
SLOT_PACKS        = (1, 3, 5)

CODE_WAIT_SECONDS     = 180
VIEW_RATE_LIMIT       = 20
VIEW_RATE_WINDOW      = 60
MAX_CAPTURES_PER_BOT  = 5000