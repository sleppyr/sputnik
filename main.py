import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from db import init_db, get_pool
from child_manager import manager
from bots.main_bot.router import router as main_bot_router

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(main_bot_router)
    dp["children"] = manager
    
    await manager.load_all()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
