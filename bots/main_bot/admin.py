from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import back_menu
from config import ADMIN_IDS
from db import get_pool
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

router = Router()

class AdminStates(StatesGroup):
    waiting_prem_id = State()
    waiting_prem_days = State()
    waiting_slots_id = State()
    waiting_slots_count = State()
    waiting_broadcast = State()

def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="👑 Выдать премиум", callback_data="adm_gift_prem")
    kb.button(text="➕ Выдать слоты", callback_data="adm_gift_slots")
    kb.button(text="📢 Рассылка", callback_data="adm_broadcast")
    kb.button(text="📊 Статистика", callback_data="adm_stats")
    kb.button(text="◀️ Назад", callback_data="main_menu")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(cb: CallbackQuery):
    if cb.from_user.id not in ADMIN_IDS:
        return await cb.answer("У вас нет доступа.", show_alert=True)
    
    text = "<b>⚙️ Админ-панель Sputnik</b>\n\nВыберите действие:"
    await cb.message.edit_text(text, reply_markup=admin_menu())
    await cb.answer()

# --- СТАТИСТИКА ---
@router.callback_query(F.data == "adm_stats")
async def cb_adm_stats(cb: CallbackQuery):
    async with get_pool().acquire() as conn:
        users = await conn.fetchval("SELECT COUNT(*) FROM owners")
        bots = await conn.fetchval("SELECT COUNT(*) FROM sub_bots")
        caps = await conn.fetchval("SELECT COUNT(*) FROM captures")
    
    text = (
        "<b>📊 Статистика системы</b>\n\n"
        f"<b>Юзеров:</b> {users}\n"
        f"<b>Ботов:</b> {bots}\n"
        f"<b>Захвачено:</b> {caps}"
    )
    await cb.message.edit_text(text, reply_markup=back_menu())
    await cb.answer()

# --- ВЫДАЧА ПРЕМИУМА ---
@router.callback_query(F.data == "adm_gift_prem")
async def cb_gift_prem(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("<b>Введите ID юзера, которому нужно выдать премиум:</b>")
    await state.set_state(AdminStates.waiting_prem_id)
    await cb.answer()

@router.message(AdminStates.waiting_prem_id)
async def process_prem_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. ID должен быть числом.")
    
    await state.update_data(target_id=user_id)
    await message.answer("<b>Введите количество дней премиума:</b>")
    await state.set_state(AdminStates.waiting_prem_days)

@router.message(AdminStates.waiting_prem_days)
async def process_prem_days(message: Message, state: FSMContext):
    try:
        days = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. Введите число.")
    
    data = await state.get_data()
    target_id = data['target_id']
    
    async with get_pool().acquire() as conn:
        # Создаем юзера если нет, и добавляем премиум
        await conn.execute(
            "INSERT INTO owners (user_id, premium_until) VALUES ($1, now() + interval '1 day' * $2) "
            "ON CONFLICT (user_id) DO UPDATE SET premium_until = COALESCE(owners.premium_until, now()) + interval '1 day' * $2",
            target_id, days
        )
    
    await message.answer(f"<b>Успешно.</b> Пользователю <code>{target_id}</code> выдан премиум на {days} дн.", reply_markup=back_menu())
    await state.clear()

# --- ВЫДАЧА СЛОТОВ ---
@router.callback_query(F.data == "adm_gift_slots")
async def cb_gift_slots(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("<b>Введите ID юзера, которому нужно добавить слоты:</b>")
    await state.set_state(AdminStates.waiting_slots_id)
    await cb.answer()

@router.message(AdminStates.waiting_slots_id)
async def process_slots_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. ID должен быть числом.")
    
    await state.update_data(target_id=user_id)
    await message.answer("<b>На сколько слотов увеличить лимит?</b>")
    await state.set_state(AdminStates.waiting_slots_count)

@router.message(AdminStates.waiting_slots_count)
async def process_slots_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. Введите число.")
    
    data = await state.get_data()
    target_id = data['target_id']
    
    async with get_pool().acquire() as conn:
        await conn.execute(
            "INSERT INTO owners (user_id, bought_slots) VALUES ($1, $2) "
            "ON CONFLICT (user_id) DO UPDATE SET bought_slots = owners.bought_slots + $2",
            target_id, count
        )
    
    await message.answer(f"<b>Успешно.</b> Пользователю <code>{target_id}</code> начислено {count} слотов.", reply_markup=back_menu())
    await state.clear()

# --- РАССЫЛКА ---
@router.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("<b>Введите текст для рассылки всем пользователям:</b>")
    await state.set_state(AdminStates.waiting_broadcast)
    await cb.answer()

@router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    text_to_send = message.text
    await message.answer("Начинаю рассылку...")
    
    async with get_pool().acquire() as conn:
        users = await conn.fetch("SELECT user_id FROM owners")
    
    success = 0
    fail = 0
    
    for u in users:
        try:
            await message.bot.send_message(u["user_id"], text_to_send)
            success += 1
            await asyncio.sleep(0.05) # защита от флуда
        except Exception:
            fail += 1
            
    await message.answer(
        f"<b>Рассылка завершена.</b>\n\n"
        f"Доставлено: {success}\n"
        f"Заблокировали бота: {fail}",
        reply_markup=back_menu()
    )
