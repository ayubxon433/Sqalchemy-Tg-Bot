
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from buttons import (
    admin_button,
    del_products_keyboard,
    edit_products_keyboard,
    edit_oneproduct_keyboard
)

from baza_qilish import (
    add_product,
    delete_product,
    get_one_product,
    edit_product_db,
    change_orders_status,
    cancel_order_db
)

from config import bot


class Mahsulot_State(StatesGroup):
    name = State()
    price = State()
    quantity = State()
    country = State()
    image = State()


class Edit_Product(StatesGroup):
    id = State()
    edit_content = State()
    new_content = State()


ADMIN_IDLARI = [5966439808, 6150566915]

admin_router = Router()


# ADMIN PANEL
@admin_router.message(F.text == '/admin')
async def admin_cmd(message: Message):
    user_id = message.from_user.id

    if user_id in ADMIN_IDLARI:
        await message.answer(
            "👑 Salom, Admin Panelga xush kelibsiz!",
            reply_markup=admin_button()
        )
    else:
        await message.answer(
            "⛔️ Siz admin emassiz!"
        )


# MAHSULOT QO'SHISH
@admin_router.callback_query(F.data == 'add-product')
async def add_product_cmd(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📦 Mahsulot nomini kiriting:"
    )

    await state.set_state(Mahsulot_State.name)
    await callback.answer()


# NOM OLISH
@admin_router.message(Mahsulot_State.name)
async def product_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Mahsulot nomini matn ko'rinishida kiriting.")
        return

    await state.update_data(name=message.text)

    await message.answer("💰 Mahsulot narxini kiriting:")
    await state.set_state(Mahsulot_State.price)


# NARX OLISH
@admin_router.message(Mahsulot_State.price)
async def product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)

        if price <= 0:
            raise ValueError

        await state.update_data(price=price)

        await message.answer("🔢 Mahsulot miqdorini kiriting:")
        await state.set_state(Mahsulot_State.quantity)

    except (ValueError, TypeError):
        await message.answer(
            "❌ Narx musbat son bo'lishi kerak."
        )


# MIQDOR OLISH
@admin_router.message(Mahsulot_State.quantity)
async def product_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)

        if quantity <= 0:
            raise ValueError

        await state.update_data(quantity=quantity)

        await message.answer(
            "🌍 Mahsulot ishlab chiqarilgan davlatni kiriting:"
        )

        await state.set_state(Mahsulot_State.country)

    except (ValueError, TypeError):
        await message.answer(
            "❌ Miqdor musbat butun son bo'lishi kerak."
        )


# DAVLAT OLISH
@admin_router.message(Mahsulot_State.country)
async def product_country(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Davlat nomini yozing.")
        return

    await state.update_data(country=message.text)

    await message.answer("🖼 Mahsulot rasmini yuboring:")
    await state.set_state(Mahsulot_State.image)


# RASM OLISH
@admin_router.message(Mahsulot_State.image)
async def product_image(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Iltimos, mahsulot rasmini yuboring.")
        return

    rasm = message.photo[-1].file_id
    data = await state.get_data()

    add_product(
        name=data["name"],
        price=data["price"],
        quantity=data["quantity"],
        country=data["country"],
        image=rasm
    )

    await message.answer_photo(
        rasm,
        caption=(
            "✅ Mahsulot muvaffaqiyatli qo'shildi!\n\n"
            f"📦 Nomi: {data['name']}\n"
            f"💰 Narxi: {data['price']}\n"
            f"🔢 Miqdori: {data['quantity']}\n"
            f"🌍 Davlati: {data['country']}"
        )
    )

    await state.clear()


# MAHSULOT O'CHIRISH MENYUSI
@admin_router.callback_query(F.data == 'del-product')
async def del_product_list(callback: CallbackQuery):
    await callback.message.edit_text(
        "🗑 Qaysi mahsulotni o'chirasiz?",
        reply_markup=del_products_keyboard()
    )

    await callback.answer()


# MAHSULOT O'CHIRISH
@admin_router.callback_query(F.data.startswith('delete:product:'))
async def delete_product__cmd(callback: CallbackQuery):
    code = int(callback.data.split(':')[2])

    delete_product(code)

    await callback.message.delete()

    await callback.message.answer(
        "✅ Mahsulot o'chirildi! Yana qaysi birini o'chirasiz?",
        reply_markup=del_products_keyboard()
    )

    await callback.answer()


# MAHSULOT YANGILASH MENYUSI
@admin_router.callback_query(F.data == 'edit-product')
async def edit_productmenu__cmd(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer(
        "✏️ Qaysi mahsulotni yangilamoqchisiz?",
        reply_markup=edit_products_keyboard()
    )

    await callback.answer()


# MAHSULOT TANLASH
@admin_router.callback_query(F.data.startswith('edit:product:'))
async def edit_product__cmd(callback: CallbackQuery):
    code = int(callback.data.split(':')[2])

    await callback.message.delete()

    await callback.message.answer(
        "⚙️ Yangilamoqchi bo'lgan ma'lumotni tanlang:",
        reply_markup=edit_oneproduct_keyboard(code)
    )

    await callback.answer()


# YANGILASHNI BEKOR QILISH
@admin_router.callback_query(F.data == 'cancel_edit_product')
async def cancel_edit_product__cmd(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer(
        "✏️ Qaysi mahsulotni yangilamoqchisiz?",
        reply_markup=edit_products_keyboard()
    )

    await callback.answer()


# YANGILANADIGAN MA'LUMOTNI TANLASH
@admin_router.callback_query(F.data.startswith('editdetailproduct:'))
async def edit_detailproduct__cmd(
    callback: CallbackQuery,
    state: FSMContext
):
    parts = callback.data.split(':')

    edit_content = parts[1]
    id_product = int(parts[2])

    await state.update_data(
        id=id_product,
        edit_content=edit_content
    )

    if edit_content == 'image':
        xabar = '🖼 Yangi rasm yuboring:'
    elif edit_content == 'name':
        xabar = '📝 Yangi nom yuboring:'
    elif edit_content == 'price':
        xabar = '💰 Yangi narx yuboring:'
    elif edit_content == 'quantity':
        xabar = '🔢 Yangi miqdor yuboring:'
    else:
        await callback.answer("❌ Noto'g'ri tanlov!")
        return

    await callback.message.answer(xabar)

    await state.set_state(Edit_Product.new_content)

    await callback.answer()


# YANGI MA'LUMOTNI OLISH
@admin_router.message(Edit_Product.new_content)
async def get_new_content(message: Message, state: FSMContext):
    data = await state.get_data()

    product_id = data.get('id')
    edit_content = data.get('edit_content')

    if edit_content == 'image':
        if not message.photo:
            await message.answer("❌ Rasm yuboring.")
            return

        new_content = message.photo[-1].file_id

    elif edit_content == 'price':
        try:
            new_content = float(message.text)

            if new_content <= 0:
                raise ValueError

        except (ValueError, TypeError):
            await message.answer("❌ Narx musbat son bo'lishi kerak.")
            return

    elif edit_content == 'quantity':
        try:
            new_content = int(message.text)

            if new_content < 0:
                raise ValueError

        except (ValueError, TypeError):
            await message.answer("❌ Miqdor 0 yoki undan katta butun son bo'lishi kerak.")
            return

    else:
        if not message.text:
            await message.answer("❌ Matn kiriting.")
            return

        new_content = message.text

    edit_product_db(
        product_id,
        edit_content,
        new_content
    )

    await message.answer(
        "✅ Mahsulot ma'lumoti yangilandi!",
        reply_markup=edit_oneproduct_keyboard(product_id)
    )

    await state.clear()


# BUYURTMANI QABUL QILISH
@admin_router.callback_query(F.data.startswith("approve_order_"))
async def approve_order_cmd(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDLARI:
        await callback.answer(
            "⛔️ Siz admin emassiz!",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    change_orders_status(user_id)

    await bot.send_message(
        user_id,
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "🛵 Tez orada yetkazib beriladi. Rahmat!"
    )

    old_text = callback.message.text or ""

    await callback.message.edit_text(
        old_text + "\n\n✅ BUYURTMA QABUL QILINGAN"
    )

    await callback.answer("Buyurtma tasdiqlandi!")


# BUYURTMANI BEKOR QILISH
@admin_router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order_cmd(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDLARI:
        await callback.answer(
            "⛔️ Siz admin emassiz!",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    cancel_order_db(user_id)

    await bot.send_message(
        user_id,
        "❌ Ming bor uzr!\n\n"
        "Buyurtmangiz bekor qilindi."
    )

    old_text = callback.message.text or ""

    await callback.message.edit_text(
        old_text + "\n\n❌ BUYURTMA BEKOR QILINGAN"
    )

    await callback.answer("Buyurtma bekor qilindi!")
