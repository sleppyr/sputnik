# child_manager.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from db import get_pool
from utils import decrypt
from bots.child_bot.router import build as build_child_router

log = logging.getLogger("child_manager")

class ChildManager:
    def __init__(self) -> None:
        self._runners: dict[int, asyncio.Task] = {}

    async def spawn(self, sub_bot_id: int, token: str) -> None:
        if sub_bot_id in self._runners:
            return
        task = asyncio.create_task(self._run(sub_bot_id, token))
        self._runners[sub_bot_id] = task

    async def _run(self, sub_bot_id: int, token: str) -> None:
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp  = Dispatcher()
        dp["bot_id"] = sub_bot_id
        dp.include_router(build_child_router(sub_bot_id))
        try:
            await dp.start_polling(bot)
        except Exception as exc:
            log.exception("child %s crashed: %s", sub_bot_id, exc)
        finally:
            await bot.session.close()
            self._runners.pop(sub_bot_id, None)

    async def stop(self, sub_bot_id: int) -> None:
        task = self._runners.pop(sub_bot_id, None)
        if task:
            task.cancel()

    async def load_all(self) -> None:
        async with get_pool().acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, token_enc FROM sub_bots WHERE is_active = TRUE"
            )
        for row in rows:
            token = decrypt(row["token_enc"])
            if token:
                await self.spawn(row["id"], token)

manager = ChildManager()
