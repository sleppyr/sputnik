import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from db import get_pool, _fernet
from bots.child_bot.router import build

class ChildManager:
    def __init__(self):
        self.runners = {}

    async def spawn(self, bot_id: int, token: str):
        if bot_id in self.runners: return
        task = asyncio.create_task(self._run(bot_id, token))
        self.runners[bot_id] = task

    async def _run(self, bot_id: int, token: str):
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        dp["bot_id"] = bot_id
        dp.include_router(build(bot_id))
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
            self.runners.pop(bot_id, None)

    async def load_all(self):
        async with get_pool().acquire() as conn:
            rows = await conn.fetch("SELECT id, token_enc FROM sub_bots")
            for r in rows:
                token = _fernet.decrypt(r["token_enc"]).decode()
                await self.spawn(r["id"], token)

manager = ChildManager()
