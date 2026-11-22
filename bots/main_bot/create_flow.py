# bots/main_bot/create_flow.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router(name="create_flow")

class CreateBot(StatesGroup):
    waiting_for_token = State()

@router.callback_query(F.data == "create_bot")
async def start_create(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        "Отправь мне токен нового бота (от BotFather).\n\n"
        "Формат: <code>123456789:AA...</code>"
    )
    await state.set_state(CreateBot.waiting_for_token)
    await cb.answer()

@router.message(CreateBot.waiting_for_token)
async def process_token(message: Message, state: FSMContext):
    token = message.text.strip()
    # Здесь будет логика проверки токена и сохранения
    await message.answer(f"Токен принят: <code>{token[:15]}...</code>\n(Логика сохранения будет дальше)")
    await state.clear()
