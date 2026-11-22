# child_bot/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_db

router = Router()

@router.message()
async def child_start(message: Message, bot_id: int) -> None:
    async with await get_db() as db:
        cur = await db.execute(
            "SELECT page_text, button_text, button_url FROM sub_bots WHERE id = ?",
            (bot_id,),
        )
        row = await cur.fetchone()
    if not row:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text=row["button_text"], url=row["button_url"])
    await message.answer(row["page_text"], reply_markup=kb.as_markup())