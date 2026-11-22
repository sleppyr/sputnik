# bots/main_bot/router.py
from aiogram import Router
from bots.main_bot import menu, create_flow, captures, admin

router = Router(name="main_bot")

router.include_router(menu.router)
router.include_router(create_flow.router)
router.include_router(captures.router)
router.include_router(admin.router)
