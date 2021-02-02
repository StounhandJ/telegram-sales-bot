from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, CommandStart
from aiogram.dispatcher.filters.builtin import CommandHelp
from data import config
from keyboards.default import menu
from keyboards.inline import choice_buttons
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(config.message["Welcome_Menu"], reply_markup=menu)


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    await message.answer("Думаю поймешь ;)")


@dp.message_handler(commands=["menu"])
async def show_menu(message: types.Message):
    await message.answer(config.message["Main_Menu"], reply_markup=menu)


@dp.message_handler(commands=["items"])
async def show_menu(message: types.Message):
    await message.answer(config.message["Product_Menu"], reply_markup=choice_buttons.getProductsKeyboard())


@dp.message_handler(Text(equals=["Список предметов"]))
async def show_product(message: types.Message):
    await message.answer(config.message["Product_Menu"], reply_markup=choice_buttons.getProductsKeyboard())


@dp.message_handler(commands=["about"])
async def show_menu(message: types.Message):
    await message.answer(config.message["About_Us"], reply_markup=menu)


@dp.message_handler(Text(equals=["О нас"]))
async def show_about(message: types.Message):
    await message.answer(config.message["About_Us"], reply_markup=menu)
