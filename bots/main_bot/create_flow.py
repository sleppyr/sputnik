from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import back_menu
from db import get_pool, _fernet
from config import FREE_BOTS

router = Router()

class CreateBot(StatesGroup):
    waiting_for_token = State()

@router.callback_query(F.data == "create_bot")
async def start_create(cb: CallbackQuery, state: FSMContext):
    async with get_pool().acquire() as conn:
        # Проверяем, есть ли слоты
        row = await conn.fetchrow("SELECT bought_slots FROM owners WHERE user_id = $1", cb.from_user.id)
        owned = await conn.fetchval("SELECT COUNT(*) FROM sub_bots WHERE owner_id = $1", cb.from_user.id)
    
    bought = row["bought_slots"] if row else 0
    total_limit = FREE_BOTS + bought
    
    if owned >= total_limit:
        text = (
            "<b>❌ Достигнут лимит ботов.</b>\n\n"
            f"У вас активно: <b>{owned}</b> из <b>{total_limit}</b> доступных.\n\n"
            "Купите слоты в магазине или активируйте премиум для расширения лимита."
        )
        return await cb.message.edit_text(text, reply_markup=back_menu())

    text = (
        "<b>➕ Создание нового бота</b>\n\n"
        "Отправьте токен нового бота.\n\n"
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
    
    async with get_pool().acquire() as conn:
        # Создаем юзера если его нет в базе, чтобы профиль работал
        await conn.execute("INSERT INTO owners (user_id) VALUES ($1) ON CONFLICT DO NOTHING", message.from_user.id)
        
        await conn.execute(
            "INSERT INTO sub_bots (owner_id, token_enc, bot_username, bot_name) "
            "VALUES ($1, $2, $3, $4)",
            message.from_user.id, token_enc, "pending_bot", "Sputnik Bot"
        )
    
    text = (
        "<b>Бот успешно добавлен в систему.</b>\n\n"
        "Теперь вы можете настроить его в меню <b>Мои боты</b>."
    )
    await message.answer(text, reply_markup=back_menu())
