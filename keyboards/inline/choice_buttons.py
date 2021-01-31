from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback
from utils.db_api import models

items = [
    {"id": 1, "name": "Алгоритмы", "price": 10000},
    {"id": 2, "name": "Мат.Анализ", "price": 75000},
    {"id": 3, "name": "Проектировани", "price": 5000},
    {"id": 4, "name": "Администрирование", "price": 3800},
    {"id": 5, "name": "РМП", "price": 12500},
]


def getSellProductsKeyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data=setting_callback.new(command="exit")),
            InlineKeyboardButton(text="Купить", callback_data=setting_callback.new(command="add"))
        ]
    ])


def getConfirmationKeyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=confirmation_callback.new(bool="Yes")),
            InlineKeyboardButton(text="Нет", callback_data=confirmation_callback.new(bool="No"))
        ]
    ])


def getProductsKeyboard():
    items = models.get_ALLProducts()
    if not items["success"]:
        return
    products = InlineKeyboardMarkup(row_width=3)
    for item in items["data"]:
        products.insert(
            InlineKeyboardButton(text=item["name"],
                                 callback_data=buy_callback.new(id=item["id"], item_name=item["name"],
                                                                price=item["price"])))
    return products
