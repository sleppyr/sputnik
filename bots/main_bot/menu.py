from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu
from config import ADMIN_IDS

router = Router()

@router.message(CommandStart())
async def start_cmd(m: Message):
    await m.answer(
        "<b>Sputnik</b>\n\n— Точность.\n— Контроль.\n\n"
        "<b>Owner:</b> @Adpuan\n<b>News:</b> @Adpianovich",
        reply_markup=main_menu(m.from_user.id in ADMIN_IDS)
    )

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    await cb.message.edit_text("Главное меню", reply_markup=main_menu(cb.from_user.id in ADMIN_IDS))
