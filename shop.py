# services/shop.py
from aiogram import Bot
from aiogram.types import (
    LabeledPrice, PreCheckoutQuery, Message, SuccessfulPayment,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import FREE_BOTS, SLOT_PRICE_STARS, SLOT_PACKS
from db import get_pool

async def owned_count(owner_id: int) -> int:
    async with get_pool().acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM sub_bots WHERE owner_id = $1", owner_id
        )

async def extra_slots(owner_id: int) -> int:
    async with get_pool().acquire() as conn:
        return await conn.fetchval(
            "SELECT COALESCE(SUM(qty),0) FROM slot_purchases WHERE owner_id = $1",
            owner_id,
        )

async def can_create(owner_id: int) -> bool:
    owned = await owned_count(owner_id)
    if owned < FREE_BOTS:
        return True
    return owned < FREE_BOTS + await extra_slots(owner_id)

def shop_menu():
    kb = InlineKeyboardBuilder()
    for qty in SLOT_PACKS:
        kb.button(
            text=f"{qty} слот(ов) — {qty * SLOT_PRICE_STARS} ⭐",
            callback_data=f"buy_slots:{qty}",
        )
    kb.button(text="◀️ Назад", callback_data="main_menu")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

async def send_invoice(bot: Bot, chat_id: int, qty: int) -> Message:
    return await bot.send_invoice(
        chat_id=chat_id,
        title="Sputnik — слоты",
        description=f"{qty} слот(ов) для ботов",
        payload=f"slots:{chat_id}:{qty}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{qty} слот(ов)",
                             amount=qty * SLOT_PRICE_STARS)],
    )

async def on_pre_checkout(q: PreCheckoutQuery) -> bool:
    try:
        _, _, qty = q.invoice_payload.split(":")
        return int(qty) in SLOT_PACKS
    except Exception:
        return False

async def on_successful_payment(p: SuccessfulPayment) -> None:
    _, owner_id, qty = p.invoice_payload.split(":")
    async with get_pool().acquire() as conn:
        await conn.execute(
            "INSERT INTO slot_purchases (owner_id, qty, stars, provider_charge_id) "
            "VALUES ($1,$2,$3,$4)",
            int(owner_id), int(qty),
            int(qty) * SLOT_PRICE_STARS,
            p.provider_payment_charge_id,
        )