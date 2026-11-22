from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import back_menu
from db import get_pool, _fernet

router = Router()

class CreateBot(StatesGroup):
    waiting_for_token = State()

@router.callback_query(F.data == "create_bot")
async def start_create(cb: CallbackQuery, state: FSMContext):
    text = (
        "<b>➕ Создание нового бота</b>\n\n"
        "Отправьте токен нового бота (получить можно у <b>@BotFather</b>).\n\n"
        "<i>Формат:</i> <code>123456789:AA...</code>"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await state.set_state(CreateBot.waiting_for_token)
    await cb.answer()

@router.message(CreateBot.waiting_for_token)
async def process_token(message: Message, state: FSMContext):
    token = message.text.strip()
    if ":" not in token:
        return await message.answer("<b>Ошибка.</b> Неверный формат токена.")
    
    await state.clear()
    token_enc = _fernet.encrypt(token.encode())
    
    # Передаем bot_name, чтобы фиксануть ошибку
    async with get_pool().acquire() as conn:
        await conn.execute(
            "INSERT INTO sub_bots (owner_id, token_enc, bot_username, bot_name) "
            "VALUES ($1, $2, $3, $4)",
            message.from_user.id, token_enc, "pending_bot", "Sputnik Bot"
        )
    
    text = (
        "<b>Бот успешно добавлен в систему.</b>\n\n"
        "Теперь вы можете настроить его текст и кнопки в меню <b>Мои боты</b>."
    )
    await message.answer(text, reply_markup=back_menu())
