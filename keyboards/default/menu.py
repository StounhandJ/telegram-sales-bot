from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список предметов"), KeyboardButton(text="О нас")],
        [KeyboardButton(text="Получить скидку"), KeyboardButton(text="Написать администрации")]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Заказы"), KeyboardButton(text="Заказы на рассмотрении")],
        [KeyboardButton(text="Сообщения от пользователей"), KeyboardButton(text="Сообщения от заказчиков")],
        [KeyboardButton(text="Отделы"), KeyboardButton(text="Промокоды")],
    ],
    resize_keyboard=True
)