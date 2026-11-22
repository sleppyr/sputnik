from aiogram import Router, F
from aiogram.types import CallbackQuery
router = Router()

@router.callback_query(F.data == "create_bot")
async def start_create(cb: CallbackQuery):
    await cb.message.edit_text("Отправь токен от BotFather:")
    await cb.answer()
