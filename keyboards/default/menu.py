from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список предметов"), KeyboardButton(text="О нас")]
    ],
    resize_keyboard=True
)
