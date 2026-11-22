# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from db import init_db, close_db
from child_manager import manager

from main_bot import router as main_bot_router
from main_bot import admin, captures, create_flow, menu

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    await init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp  = Dispatcher()
    dp.include_router(main_bot_router)
    dp.include_router(create_flow.router)
    dp.include_router(captures.router)
    dp.include_router(admin.router)
    dp.include_router(menu.router)
    dp["children"] = manager
    await manager.load_all()
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())