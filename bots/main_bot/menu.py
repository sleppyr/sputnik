# bots/main_bot/menu.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu, back_menu
from config import ADMIN_IDS, FREE_BOTS
from db import get_pool
from shop import shop_menu 

router = Router()

GREETING = (
    "<b>Добро пожаловать в Sputnik.</b>\n\n"
    "<blockquote>Инструмент для тех, кто ценит точность и контроль.</blockquote>\n\n"
    f"Первые <b>{FREE_BOTS}</b> бота — безвозмездно.\n"
    "Далее — по билету (79 ⭐ за слот).\n\n"
    "<b>Owner:</b> @Adpuan\n"
    "<b>News:</b> @Adpianovich"
)

@router.message(CommandStart())
async def start_cmd(m: Message):
    async with get_pool().acquire() as conn:
        await conn.execute("INSERT INTO owners (user_id) VALUES ($1) ON CONFLICT DO NOTHING", m.from_user.id)
    await m.answer(GREETING, reply_markup=main_menu(m.from_user.id in ADMIN_IDS))

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    await cb.message.edit_text(GREETING, reply_markup=main_menu(cb.from_user.id in ADMIN_IDS))
    await cb.answer()

# --- МОИ БОТЫ ---
@router.callback_query(F.data == "my_bots")
async def cb_my_bots(cb: CallbackQuery):
    async with get_pool().acquire() as conn:
        bots = await conn.fetch("SELECT id, bot_username FROM sub_bots WHERE owner_id = $1", cb.from_user.id)
    
    if not bots:
        await cb.message.edit_text("У вас пока нет созданных ботов.", reply_markup=back_menu())
        return await cb.answer()
    
    text = "<b>🤖 Ваши боты:</b>\n\n"
    for b in bots:
        text += f"— @{b['bot_username']} (ID: <code>{b['id']}</code>)\n"
    
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()

# --- СТАТИСТИКА ---
@router.callback_query(F.data == "stats")
async def cb_stats(cb: CallbackQuery):
    async with get_pool().acquire() as conn:
        owned = await conn.fetchval("SELECT COUNT(*) FROM sub_bots WHERE owner_id = $1", cb.from_user.id)
        total_caps = await conn.fetchval(
            "SELECT COUNT(*) FROM captures c JOIN sub_bots b ON c.sub_bot_id = b.id WHERE b.owner_id = $1", 
            cb.from_user.id
        )
    
    text = (
        "<b>📊 Ваша статистика</b>\n\n"
        f"<b>Создано ботов:</b> {owned}\n"
        f"<b>Всего переходов:</b> {total_caps or 0}\n"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()

# --- О ПРОЕКТЕ ---
@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery):
    text = (
        "<b>ℹ️ О проекте Sputnik</b>\n\n"
        "Наш сервис предоставляет мощные инструменты для создания и управления ботами.\n\n"
        "<b>Связь с администрацией:</b>\n"
        "<b>Owner:</b> @Adpuan\n"
        "<b>News:</b> @Adpianovich"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()

# --- МАГАЗИН ---
@router.callback_query(F.data == "shop")
async def cb_shop_redirect(cb: CallbackQuery):
    await cb.message.edit_text("💎 <b>Магазин Sputnik</b>", reply_markup=shop_menu())
    await cb.answer()

# --- ПРОФИЛЬ ---
@router.callback_query(F.data == "profile")
async def cb_profile(cb: CallbackQuery):
    async with get_pool().acquire() as conn:
        row = await conn.fetchrow("SELECT premium_until, bought_slots FROM owners WHERE user_id = $1", cb.from_user.id)
        owned = await conn.fetchval("SELECT COUNT(*) FROM sub_bots WHERE owner_id = $1", cb.from_user.id)
    
    bought = row["bought_slots"] if row else 0
    total_limit = FREE_BOTS + bought
    prem_status = "❌ Нет"
    
    if row and row["premium_until"]:
        prem_status = f"✅ До {row['premium_until'].strftime('%Y-%m-%d')}"

    text = (
        "<b>👤 Ваш профиль</b>\n\n"
        f"<b>ID:</b> <code>{cb.from_user.id}</code>\n"
        f"<b>Имя:</b> {cb.from_user.full_name}\n"
        f"<b>Ботов:</b> {owned} / {total_limit}\n"
        f"<b>Премиум:</b> {prem_status}\n\n"
        f"<i>Для покупки слотов перейдите в магазин.</i>"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()
