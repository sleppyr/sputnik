from aiogram import Router
from aiogram.types import Message
router = Router()
@router.message()
async def start(m: Message):
    await m.answer("Подтвердите вход.")
