from aiogram import types

from data import config
from keyboards.default.menu import admin_menu
from loader import dp


### Помощь ###

@dp.message_handler(user_id=config.ADMINS, commands=["Ahelp", "ahelp", "helpA", "helpAdmin", "helpa", "helpadmin"])
async def show_help(message: types.Message):
    await message.answer(config.adminMessage["help"], reply_markup=admin_menu)


@dp.message_handler(user_id=config.ADMINS, commands=["Akeyboard"])
async def show_help(message: types.Message):
    await message.answer("Клавитатура админа установлена", reply_markup=admin_menu)