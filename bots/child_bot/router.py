# bots/child_bot/router.py
from aiogram import Router
from bots.child_bot import start, code_entry, session_flow

def build(bot_id: int) -> Router:
    r = Router(name=f"child_{bot_id}")
    r.include_router(start.router)
    r.include_router(code_entry.router)
    r.include_router(session_flow.router)
    return r
