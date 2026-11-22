import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "9244049233:AAFNOulqSA8d2l1T6XR4yc6eDX_pEh8WMkk")
FERNET_KEY = os.getenv("FERNET_KEY", "uQjy9RTlX0mvqcFtkDsCrq-lxrOI8Z0CWFX2Rz0aNbM=")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:pGWXfnllqtMLfjZmlESVTkQCfgpkMKaw@autorack.proxy.rlwy.net:53746/railway")

ADMIN_IDS = {8517129681}
FREE_BOTS = 3
