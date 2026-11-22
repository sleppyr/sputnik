# main_bot/menu.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS, FREE_BOTS

router = Router()

GREETING = (
    "Добро пожаловать в <b>Sputnik</b>.\n\n"
    "Инструмент для тех, кто ценит точность.\n\n"
    "— Создавайте ботов\n"
    "— Наблюдайте за потоком\n"
    "— Управляйте доступом\n\n"
    f"Первые {FREE_BOTS} бота — безвозмездно.\n"
    "Далее — по билету."
)

def main_menu(is_admin: bool = False):
    kb = InlineKeyboardBuilder()
    kb.button(text="Мои боты", callback_data="my_bots")
    kb.button(text="Создать", callback_data="create_bot")
    kb.button(text="Статистика", callback_data="stats")
    kb.button(text="Магазин", callback_data="shop")
    if is_admin:
        kb.button(text="Админ-панель", callback_data="admin_panel")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

@router.message(CommandStart())
async def start(message: Message):
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        f"{GREETING}\n\n"
        "<b>Owner:</b> @Adpuan\n"
        "<b>News:</b> @Adpianovich",
        reply_markup=main_menu(is_admin)
    )