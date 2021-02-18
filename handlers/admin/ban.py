from aiogram import types

from data import config
from loader import dp
from utils.db_api.models import banListModel
from utils import function


@dp.message_handler(user_id=config.ADMINS, commands=["banList"])
async def show_codeList(message: types.Message):
    banList = banListModel.get_all_ban()
    mes = "Никто не забанен"
    form = "{number}. ID {id}"
    if banList["code"] == 200:
        mes = "Список забаненых:\n"
        for number, ban in enumerate(banList["data"]):
            mes += form.format(number=number+1, id=ban["userID"])
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["ban"])
async def show_codeList(message: types.Message):
    userID = function.checkID(message.text)
    mes = "Вы указали неверный ID"
    if userID > 0:
        mes = "Пользователь заблокирован"
        banListModel.add_ban(userID)
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["unban"])
async def show_codeList(message: types.Message):
    userID = function.checkID(message.text)
    mes = "Вы указали неверный ID"
    if userID > 0:
        mes = "Пользователь разблокирован"
        banListModel.del_ban(userID)
    await message.answer(mes)
