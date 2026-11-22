from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_pool
from config import PREM_1D, PREM_3D, PREM_14D, PREMIUM_PACKS, BASIC_PACK

router = Router()

def shop_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text=f"1 день — {PREM_1D} ⭐", callback_data=f"buy_prem:{PREM_1D}:1")
    kb.button(text=f"3 дня — {PREM_3D} ⭐", callback_data=f"buy_prem:{PREM_3D}:3")
    kb.button(text=f"14 дней — {PREM_14D} ⭐", callback_data=f"buy_prem:{PREM_14D}:14")
    kb.button(text="◀️ Назад", callback_data="main_menu")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery):
    text = (
        "<b>💎 Магазин Sputnik</b>\n\n"
        "Премиум открывает доступ к эксклюзивным пакам и увеличивает лимит ботов.\n\n"
        "<b>Доступные паки в премиуме:</b>\n"
        + "\n".join([f"— {pack}" for pack in PREMIUM_PACKS])
    )
    await cb.message.edit_text(text, reply_markup=shop_menu())
    await cb.answer()

@router.callback_query(F.data.startswith("buy_prem:"))
async def buy_prem(cb: CallbackQuery):
    _, price, days = cb.data.split(":")
    price, days = int(price), int(days)
    
    await cb.message.answer_invoice(
        title=f"Премиум на {days} дней",
        description=f"Доступ к {len(PREMIUM_PACKS)} эксклюзивным пакам и слотам.",
        payload=f"premium:{days}",
        currency="XTR",
        prices=[LabeledPrice(label="Премиум", amount=price)]
    )
    await cb.answer()

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def on_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("premium:"):
        days = int(payload.split(":")[1])
        async with get_pool().acquire() as conn:
            # Добавляем дни к премиуму
            await conn.execute(
                "INSERT INTO owners (user_id, premium_until) VALUES ($1, now() + interval '1 day' * $2) "
                "ON CONFLICT (user_id) DO UPDATE SET premium_until = owners.premium_until + interval '1 day' * $2",
                message.from_user.id, days
            )
        await message.answer("<b>Оплата прошла успешно.</b> Премиум активирован!")
