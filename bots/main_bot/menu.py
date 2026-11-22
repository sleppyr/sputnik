from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu, back_menu
from config import ADMIN_IDS, FREE_BOTS
from db import get_pool

router = Router()

GREETING = (
    "<b>Добро пожаловать в Sputnik.</b>\n\n"
    "<blockquote>Инструмент для тех, кто ценит точность и контроль.</blockquote>\n\n"
    "<b>— Создавайте ботов</b>\n"
    "<b>— Наблюдайте за потоком</b>\n"
    "<b>— Управляйте доступом</b>\n\n"
    f"Первые <b>{FREE_BOTS}</b> бота — безвозмездно.\n"
    "Далее — по билету (79 ⭐ за слот).\n\n"
    "<b>Owner:</b> @Adpuan\n"
    "<b>News:</b> @Adpianovich"
)

@router.message(CommandStart())
async def start_cmd(m: Message):
    await m.answer(GREETING, reply_markup=main_menu(m.from_user.id in ADMIN_IDS))

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    await cb.message.edit_text(GREETING, reply_markup=main_menu(cb.from_user.id in ADMIN_IDS))
    await cb.answer()

@router.callback_query(F.data == "profile")
async def cb_profile(cb: CallbackQuery):
    async with get_pool().acquire() as conn:
        owned = await conn.fetchval("SELECT COUNT(*) FROM sub_bots WHERE owner_id = $1", cb.from_user.id)
    
    text = (
        "<b>👤 Ваш профиль</b>\n\n"
        f"<b>ID:</b> <code>{cb.from_user.id}</code>\n"
        f"<b>Имя:</b> {cb.from_user.full_name}\n"
        f"<b>Активных ботов:</b> {owned} / {FREE_BOTS + 0}\n\n" # 0 - купленные слоты
        f"<i>Для расширения лимита перейдите в магазин.</i>"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()

@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery):
    text = (
        "<b>ℹ️ О проекте Sputnik</b>\n\n"
        "Наш сервис предоставляет мощные инструменты для создания и управления ботами.\n\n"
        "<b>Связь с администрацией:</b>\n"
        "Owner: @Adpuan\n"
        "News: @Adpianovich"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()
