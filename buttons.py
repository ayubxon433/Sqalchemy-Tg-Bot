
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder
)

from baza_qilish import get_all_products, get_one_product


# START MENYU
def start_btn():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='🛍 Mahsulotlar',
        callback_data='products'
    )

    builder.button(
        text='🍽 Taomlar',
        callback_data='taomlar'
    )

    builder.button(
        text='🛒 Savat',
        callback_data='cart'
    )

    builder.button(
        text='📋 Buyurtmalar tarixi',
        callback_data='order_history'
    )

    builder.adjust(1)
    return builder.as_markup()


# MAHSULOTLAR
def products_keyboard():
    builder = InlineKeyboardBuilder()

    products = get_all_products()

    for i in products:
        builder.button(
            text=f"📦 {i.name}",
            callback_data=f"product_{i.id}"
        )

    builder.button(
        text='🔙 Ortga',
        callback_data='back'
    )

    builder.adjust(1)
    return builder.as_markup()


# MAHSULOT O'CHIRISH
def del_products_keyboard():
    builder = InlineKeyboardBuilder()

    products = get_all_products()

    for i in products:
        builder.button(
            text=f'🗑 {i.name}',
            callback_data=f"delete:product:{i.id}"
        )

    builder.button(
        text='🔙 Ortga',
        callback_data='back'
    )

    builder.adjust(1)
    return builder.as_markup()


# MAHSULOT TANLASH
def back_button(id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🛒 Buyurtma qilish",
        callback_data=f'order:{id}'
    )

    builder.button(
        text='🔙 Ortga',
        callback_data='back-mahsulotlar'
    )

    builder.adjust(1)
    return builder.as_markup()


# ADMIN PANEL
def admin_button():
    builder = InlineKeyboardBuilder()

    builder.button(
        text='➕ Mahsulot qo`shish',
        callback_data='add-product'
    )

    builder.button(
        text='✏️ Mahsulot yangilash',
        callback_data='edit-product'
    )

    builder.button(
        text='🗑 Mahsulot o`chirish',
        callback_data='del-product'
    )

    builder.adjust(1)
    return builder.as_markup()


# MAHSULOT YANGILASH RO'YXATI
def edit_products_keyboard():
    builder = InlineKeyboardBuilder()

    products = get_all_products()

    for i in products:
        builder.button(
            text=f'✏️ {i.name}',
            callback_data=f"edit:product:{i.id}"
        )

    builder.button(
        text='🔙 Ortga',
        callback_data='back'
    )

    builder.adjust(1)
    return builder.as_markup()


# BITTA MAHSULOTNI YANGILASH
def edit_oneproduct_keyboard(code):
    builder = InlineKeyboardBuilder()

    mahsulot = get_one_product(code)

    builder.button(
        text='🖼 Rasm',
        callback_data=f'editdetailproduct:image:{code}'
    )

    builder.button(
        text=f'📝 Nomi: {mahsulot.name}',
        callback_data=f'editdetailproduct:name:{code}'
    )

    builder.button(
        text=f'💰 Narxi: {mahsulot.price}',
        callback_data=f'editdetailproduct:price:{code}'
    )

    builder.button(
        text=f'🔢 Miqdori: {mahsulot.quantity}',
        callback_data=f'editdetailproduct:quantity:{code}'
    )

    builder.button(
        text='❌ Bekor qilish',
        callback_data='cancel_edit_product'
    )

    builder.adjust(1)
    return builder.as_markup()


# SAVAT TUGMALARI
def savat_button():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Tasdiqlash",
        callback_data='doorder'
    )

    builder.button(
        text="🗑 Tozalash",
        callback_data="cancelorder"
    )

    builder.button(
        text="🔙 Ortga",
        callback_data="back"
    )

    builder.adjust(1)
    return builder.as_markup()


# TELEFON RAQAMINI YUBORISH
def phone_button():
    builder = ReplyKeyboardBuilder()

    builder.button(
        text="📱 Telefon raqamni yuborish",
        request_contact=True
    )

    builder.adjust(1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


# TELEFON TUGMASINI YOPISH UCHUN
def remove_phone_button():
    from aiogram.types import ReplyKeyboardRemove

    return ReplyKeyboardRemove()


# ADMIN BUYURTMA TUGMALARI
def order_button(order_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Buyurtmani qabul qilish",
        callback_data=f"approve_order_{order_id}"
    )

    builder.button(
        text="❌ Buyurtmani bekor qilish",
        callback_data=f"cancel_order_{order_id}"
    )

    builder.adjust(1)

    return builder.as_markup()
