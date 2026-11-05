
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from buttons import (
    start_btn,
    products_keyboard,
    back_button,
    savat_button,
    order_button,
    phone_button,
    remove_phone_button
)

from baza_qilish import (
    get_one_product,
    add_order,
    buyurtmalar_olish,
    buyurtmalar_ochirish,
    confirm_order,
    get_order_history
)

from config import bot


router = Router()

GROUP_ID = -5565938134


# MIJOZ MA'LUMOTLARI HOLATLARI
class OrderState(StatesGroup):
    ism = State()
    telefon = State()
    manzil = State()


# START
@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Menyuni tanlang:",
        reply_markup=start_btn()
    )


# MAHSULOTLAR
@router.callback_query(F.data == "products")
async def products_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 Barcha mahsulotlar:",
        reply_markup=products_keyboard()
    )
    await callback.answer()


# BITTA MAHSULOT
@router.callback_query(F.data.startswith('product_'))
async def product__cmd(callback: CallbackQuery):
    code = int(callback.data.split('_')[1])

    product = get_one_product(code)

    if not product:
        await callback.answer(
            "❌ Mahsulot topilmadi!",
            show_alert=True
        )
        return

    xabar = f"""📦 Tanlangan mahsulot:

📝 Nomi: {product.name}
💰 Narxi: {product.price} so'm
🔢 Ombordagi miqdori: {product.quantity}
🌍 Davlat: {product.country}
"""

    await callback.message.delete()

    await callback.message.answer_photo(
        product.image,
        caption=xabar,
        reply_markup=back_button(code)
    )

    await callback.answer()


# SAVATGA QO'SHISH
@router.callback_query(F.data.startswith('order:'))
async def add_order__cmd(callback: CallbackQuery):
    code = int(callback.data.split(':')[1])

    mahsulot = get_one_product(code)

    if not mahsulot:
        await callback.answer(
            "❌ Mahsulot topilmadi!",
            show_alert=True
        )
        return

    add_order(
        callback.from_user.id,
        code,
        1,
        mahsulot.price
    )

    await callback.answer(
        f"✅ {mahsulot.name} savatga qo'shildi!",
        show_alert=True
    )


# ASOSIY MENYUGA QAYTISH
@router.callback_query(F.data == 'back')
async def back_cmd(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔙 Asosiy menyuga qaytdingiz.",
        reply_markup=start_btn()
    )
    await callback.answer()


# MAHSULOTLAR RO'YXATIGA QAYTISH
@router.callback_query(F.data == 'back-mahsulotlar')
async def back_mahsulotlar_cmd(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer(
        "📦 Mahsulotlar ro'yxati:",
        reply_markup=products_keyboard()
    )

    await callback.answer()


# SAVAT
@router.callback_query(F.data == "cart")
async def cart_cmd(callback: CallbackQuery):
    user_id = callback.from_user.id

    buyurtmalar = buyurtmalar_olish(user_id)

    if not buyurtmalar:
        await callback.answer(
            "🛒 Savatingiz hozircha bo'sh!",
            show_alert=True
        )
        return

    text = "🛒 SIZNING SAVATINGIZ\n"
    text += "━━━━━━━━━━━━━━━━━━\n"

    umumiy_summa = 0

    for i in buyurtmalar:
        mahsulot = get_one_product(i.mahsulot)

        if not mahsulot:
            continue

        text += (
            f"\n📦 Mahsulot: {mahsulot.name}\n"
            f"💰 Bir dona narxi: {mahsulot.price:,.0f} so'm\n"
            f"🔢 Miqdori: {i.miqdori} ta\n"
            f"💵 Jami: {i.summa:,.0f} so'm\n"
            "━━━━━━━━━━━━━━━━━━\n"
        )

        umumiy_summa += i.summa

    text += f"\n💰 UMUMIY SUMMA: {umumiy_summa:,.0f} so'm"

    await callback.message.delete()

    await callback.message.answer(
        text,
        reply_markup=savat_button()
    )

    await callback.answer()


# BUYURTMANI TASDIQLASHNI BOSHLASH
@router.callback_query(F.data == "doorder")
async def doorder_cmd(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    buyurtmalar = buyurtmalar_olish(user_id)

    if not buyurtmalar:
        await callback.answer(
            "❌ Savatingiz bo'sh!",
            show_alert=True
        )
        return

    await state.clear()

    await state.set_state(OrderState.ism)

    await callback.message.delete()

    await callback.message.answer(
        "👤 Buyurtma berish uchun ism va familiyangizni kiriting:"
    )

    await callback.answer()


# ISM OLISH
@router.message(OrderState.ism)
async def get_order_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer(
            "❌ Iltimos, ism va familiyangizni to'g'ri kiriting."
        )
        return

    await state.update_data(
        ism=message.text.strip()
    )

    await state.set_state(OrderState.telefon)

    await message.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=phone_button()
    )


# TELEFON RAQAMINI OLISH
@router.message(OrderState.telefon)
async def get_order_phone(message: Message, state: FSMContext):
    telefon = None

    if message.contact:
        # Boshqa odamning kontaktini yuborishni cheklaymiz
        if message.contact.user_id != message.from_user.id:
            await message.answer(
                "❌ Iltimos, o'zingizning telefon raqamingizni yuboring."
            )
            return

        telefon = message.contact.phone_number

    elif message.text:
        telefon = message.text.strip()

    if not telefon:
        await message.answer(
            "❌ Telefon raqamingizni yuboring yoki yozing."
        )
        return

    await state.update_data(
        telefon=telefon
    )

    await state.set_state(OrderState.manzil)

    await message.answer(
        "📍 Yetkazib berish manzilingizni to'liq yozing:",
        reply_markup=remove_phone_button()
    )


# MANZIL OLISH VA BUYURTMANI YUBORISH
@router.message(OrderState.manzil)
async def get_order_address(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 5:
        await message.answer(
            "❌ Iltimos, manzilingizni to'liq kiriting."
        )
        return

    user_id = message.from_user.id

    data = await state.get_data()

    ism = data['ism']
    telefon = data['telefon']
    manzil = message.text.strip()

    # SAVATDAGI MAHSULOTLARNI OLISH
    buyurtmalar = buyurtmalar_olish(user_id)

    if not buyurtmalar:
        await message.answer(
            "❌ Savatingiz bo'sh. Buyurtma berish amalga oshmadi.",
            reply_markup=start_btn()
        )
        await state.clear()
        return

    # GURUHGA YUBORILADIGAN XABAR
    text = "🔔 YANGI BUYURTMA!\n"
    text += "━━━━━━━━━━━━━━━━━━\n\n"

    text += (
        f"👤 Mijoz: {ism}\n"
        f"📱 Telefon: {telefon}\n"
        f"📍 Manzil: {manzil}\n"
        f"🆔 Telegram ID: {user_id}\n\n"
    )

    text += "🛒 BUYURTMALAR:\n"
    text += "━━━━━━━━━━━━━━━━━━\n"

    umumiy_summa = 0

    for i in buyurtmalar:
        mahsulot = get_one_product(i.mahsulot)

        if not mahsulot:
            continue

        text += (
            f"\n📦 Mahsulot: {mahsulot.name}\n"
            f"💰 Narxi: {mahsulot.price:,.0f} so'm\n"
            f"🔢 Miqdori: {i.miqdori} ta\n"
            f"💵 Jami: {i.summa:,.0f} so'm\n"
            "--------------------------\n"
        )

        umumiy_summa += i.summa

    text += (
        f"\n💰 UMUMIY SUMMA: {umumiy_summa:,.0f} so'm\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    # MA'LUMOTLARNI BAZAGA SAQLASH
    result = confirm_order(
        user_id,
        ism,
        telefon,
        manzil
    )

    if not result:
        await message.answer(
            "❌ Buyurtmani saqlashda xatolik yuz berdi.",
            reply_markup=start_btn()
        )
        await state.clear()
        return

    # GURUHGA YUBORISH
    try:
        await bot.send_message(
            GROUP_ID,
            text,
            reply_markup=order_button(user_id)
        )

    except Exception:
        await message.answer(
            "⚠️ Buyurtma bazaga saqlandi, lekin guruhga yuborilmadi. "
            "Admin botning guruhdagi huquqlarini tekshirsin.",
            reply_markup=start_btn()
        )
        await state.clear()
        return

    await message.answer(
        "✅ BUYURTMANGIZ MUVAFFAQIYATLI QABUL QILINDI!\n\n"
        f"👤 Ism: {ism}\n"
        f"📱 Telefon: {telefon}\n"
        f"📍 Manzil: {manzil}\n\n"
        "Tez orada siz bilan bog'lanamiz. 😊",
        reply_markup=start_btn()
    )

    await state.clear()


# SAVATNI TOZALASH
@router.callback_query(F.data == "cancelorder")
async def cancelorder_cmd(callback: CallbackQuery):
    user_id = callback.from_user.id

    buyurtmalar_ochirish(user_id)

    await callback.message.delete()

    await callback.message.answer(
        "🗑 Savatingiz tozalandi!",
        reply_markup=start_btn()
    )

    await callback.answer()


# BUYURTMALAR TARIXI
@router.callback_query(F.data == "order_history")
async def order_history_cmd(callback: CallbackQuery):
    user_id = callback.from_user.id

    buyurtmalar = get_order_history(user_id)

    if not buyurtmalar:
        await callback.answer(
            "📋 Sizda hali tasdiqlangan buyurtmalar mavjud emas.",
            show_alert=True
        )
        return

    text = "📋 BUYURTMALAR TARIXI\n"
    text += "━━━━━━━━━━━━━━━━━━\n"

    for i in buyurtmalar:
        mahsulot = get_one_product(i.mahsulot)

        if not mahsulot:
            continue

        if i.status == "pending":
            status = "⏳ Kutilmoqda"
        elif i.status == "accepted":
            status = "✅ Qabul qilingan"
        elif i.status == "cancelled":
            status = "❌ Bekor qilingan"
        else:
            status = "Noma'lum"

        text += (
            f"\n🆔 Buyurtma: #{i.id}\n"
            f"📦 Mahsulot: {mahsulot.name}\n"
            f"🔢 Miqdori: {i.miqdori} ta\n"
            f"💰 Jami: {i.summa:,.0f} so'm\n"
            f"📅 Sana: {i.vaqt.strftime('%d.%m.%Y %H:%M')}\n"
            f"📌 Holati: {status}\n"
            "━━━━━━━━━━━━━━━━━━\n"
        )

    await callback.message.delete()

    await callback.message.answer(
        text,
        reply_markup=start_btn()
    )

    await callback.answer()
