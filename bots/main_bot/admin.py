from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import back_menu
from config import ADMIN_IDS
from db import get_pool

router = Router()

@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(cb: CallbackQuery):
    if cb.from_user.id not in ADMIN_IDS:
        return await cb.answer("У вас нет доступа.", show_alert=True)
    
    async with get_pool().acquire() as conn:
        users_count = await conn.fetchval("SELECT COUNT(*) FROM sub_bots")
    
    text = (
        "<b>⚙️ Админ-панель Sputnik</b>\n\n"
        f"<b>Всего ботов в системе:</b> {users_count}\n\n"
        "<i>Управление пользователями, рассылка и логи доступны по API.</i>"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()
