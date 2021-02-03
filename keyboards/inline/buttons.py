from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback
from utils.db_api.models import productModel


def getSellProductsKeyboard(productID):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data=setting_callback.new(command="exit", productID=-1)),
            InlineKeyboardButton(text="Купить", callback_data=setting_callback.new(command="add", productID=productID))
        ]
    ])


def getConfirmationKeyboard(**kwargs):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=confirmation_callback.new(bool="Yes")),
            InlineKeyboardButton(text="Нет", callback_data=confirmation_callback.new(bool="No"))
        ]])
    for arg, text in kwargs.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=confirmation_callback.new(bool=arg)))
    return keyboard


def getProductsKeyboard():
    items = productModel.get_ALLProducts()
    if not items["success"]:
        return
    products = InlineKeyboardMarkup(row_width=3)
    for item in items["data"]:
        products.insert(
            InlineKeyboardButton(text=item["name"],
                                 callback_data=buy_callback.new(id=item["id"], item_name=item["name"],
                                                                price=item["price"])))
    return products
