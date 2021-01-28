from textwrap import wrap
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback

items = [
    {"name": "Алгоритмы", "price": 10000},
    {"name": "Мат.Анализ", "price": 75000},
    {"name": "Проектировани", "price": 5000},
    {"name": "Администрирование", "price": 3800},
    {"name": "РМП", "price": 12500},
]
products = InlineKeyboardMarkup(row_width=3)
for item in items:
    price = ""
    temporaryArrayNumbers = wrap(str(item["price"])[::-1], 3)
    temporaryArrayNumbers.reverse()
    for numbers in temporaryArrayNumbers:
        price += numbers[::-1] + " "
    products.insert(
        InlineKeyboardButton(text=item["name"], callback_data=buy_callback.new(item_name=item["name"], price=price+"р.")))

sell_products_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Назад", callback_data=setting_callback.new(command="exit")),
        InlineKeyboardButton(text="Купить", callback_data=setting_callback.new(command="add"))
    ]
])

confirmation = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Да", callback_data=confirmation_callback.new(bool="Yes")),
        InlineKeyboardButton(text="Нет", callback_data=confirmation_callback.new(bool="No"))
    ]
])
