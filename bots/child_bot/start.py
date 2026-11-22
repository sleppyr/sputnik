# bots/child_bot/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_pool

router = Router()

@router.message()
async def child_start(message: Message, bot_id: int) -> None:
    async with get_pool().acquire() as conn:
        row = await conn.fetchrow(
            "SELECT page_text, button_text, button_url FROM sub_bots WHERE id = $1",
            bot_id
        )
    if not row:
        return
    
    kb = InlineKeyboardBuilder()
    kb.button(text=row["button_text"], url=row["button_url"])
    await message.answer(row["page_text"], reply_markup=kb.as_markup())
