from aiogram import types
from aiogram.dispatcher import FSMContext
from data import config
from datetime import datetime
from states.admin_mes_user import AdminMesUser
from keyboards.inline import choice_buttons
from keyboards.inline.callback_datas import confirmation_callback
from keyboards.default import menu
from loader import dp, bot
from utils.db_api import models


@dp.message_handler(user_id=config.ADMINS, commands=["ordermes", "mesorder"])
async def order_messages(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    messages = models.get_order_messages()
    if messages["success"]:
        mes = config.adminMessage["messages_main_order"]
        num = 1
        for item in messages["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            mes += config.adminMessage["messages_info"].format(num=num, id=item["id"], date=dateMes)
            num += 1
    else:
        mes = config.adminMessage["messages_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["allmes", "mesall"])
async def all_messages(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    messages = models.get_all_messages()
    if messages["success"]:
        mes = config.adminMessage["messages_main_all"]
        num = 1
        for item in messages["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            mes += config.adminMessage["messages_info"].format(num=num, id=item["id"], date=dateMes)
            num += 1
    else:
        mes = config.adminMessage["messages_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["mesinfo", "infomes"])
async def show_info_order(message: types.Message):
    mes = "Данное сообщние не найдено"
    messageInfo = models.get_message(checkID(message.text))
    if messageInfo["success"]:
        mes = config.adminMessage["message_detailed_info"].format(id=messageInfo["id"], text=messageInfo["message"],
                                                                  date=datetime.utcfromtimestamp(
                                                                      messageInfo["date"]).strftime(
                                                                      '%Y-%m-%d %H:%M:%S'))
        mes += "Сообщение от " + ("пользователя с заказом" if messageInfo["isOrder"] else "обычного пользователя")
        mes += "\n<b>На сообщение уже ответили</b>" if not messageInfo["active"] else ""
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["usend", "usersend", "sendu", "usenduser"])
async def message_send_start(message: types.Message, state: FSMContext):
    mes = config.adminMessage["message_missing"]
    messageInfo = models.get_message(checkID(message.text))
    if messageInfo["success"] and not messageInfo["active"]:
        mes = config.adminMessage["order_completed"]
    elif messageInfo["success"]:
        async with state.proxy() as data:
            data["message_sendID"] = messageInfo["id"]
        await AdminMesUser.message.set()
        mes = config.adminMessage["message_send"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=AdminMesUser.message, user_id=config.ADMINS)
async def message_add_mes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mes = data.get("message") if "message" in data.keys() else ""
    async with state.proxy() as data:
        data["message"] = mes + message.text + "\n"
    await message.answer(message.text + "\nПодтверждаете?",
                         reply_markup=choice_buttons.getConfirmationKeyboard(cancel="Отменить"))
    await AdminMesUser.wait.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesUser.wait)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = config.adminMessage["message_completed"]
    data = await state.get_data()
    messageInfo = models.get_message(data.get("message_sendID"))
    text = data.get("message") if "message" in data.keys() else ""
    if messageInfo["success"] and messageInfo["active"]:
        await bot.send_message(chat_id=messageInfo["userID"], text=text, reply_markup=menu)
        models.updateActive_message(data.get("message_sendID"))
        mes = config.adminMessage["message_yes_send"]
    await call.message.edit_text(mes)
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesUser.wait)
async def comment_confirmation_no(call: types.CallbackQuery):
    await call.message.edit_text(config.message["message_no"])
    await AdminMesUser.message.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminMesUser.wait)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["message_cancel"])
    await state.finish()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
