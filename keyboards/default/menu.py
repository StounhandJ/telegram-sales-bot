from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список предметов"), KeyboardButton(text="О нас")],
        [KeyboardButton(text="Написать администрации")]
    ],
    resize_keyboard=True
)
