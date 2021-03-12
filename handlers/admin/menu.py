from aiogram import types

from data import config
from keyboards.default.menu import admin_menu
from loader import dp
from utils.telegram_files import TelegramFiles


### Помощь ###

@dp.message_handler(user_id=config.ADMINS, commands=["Ahelp", "ahelp", "helpA", "helpAdmin", "helpa", "helpadmin"])
async def show_help(message: types.Message):
    await message.answer(config.adminMessage["help"], reply_markup=admin_menu)


@dp.message_handler(user_id=config.ADMINS, commands=["Akeyboard"])
async def show_help(message: types.Message):
    await message.answer("Клавитатура админа установлена", reply_markup=admin_menu)


@dp.message_handler(user_id=config.ADMINS, commands=["testD"])
async def bot_start(message: types.Message):
    await message.answer_document(caption=config.message["confirmations_agreement"], document=await TelegramFiles.get_telegram_key_files("documents/test.txt", message.chat.id))


@dp.message_handler(user_id=config.ADMINS, commands=["testI"])
async def bot_start(message: types.Message):
    await message.answer_photo(caption=config.message["confirmations_agreement"], photo=await TelegramFiles.get_telegram_key_files("images/test.png", message.chat.id))