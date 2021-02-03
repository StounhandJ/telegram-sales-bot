from aiogram import types
from aiogram.dispatcher import FSMContext
from data import config
from datetime import datetime
from states.admin_mes_user import AdminMesUser
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from keyboards.default.menu import menu
from loader import dp, bot
from utils.db_api.models import messagesModel


@dp.message_handler(user_id=config.ADMINS, commands=["ordermes", "mesorder"])
async def order_messages(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    messages = messagesModel.get_order_messages()
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
    messages = messagesModel.get_all_messages()
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
async def show_info_mes(message: types.Message):
    mes = "Данное сообщние не найдено"
    messageInfo = messagesModel.get_message(checkID(message.text))
    if messageInfo["success"]:
        mes = config.adminMessage["message_detailed_info"].format(id=messageInfo["id"], text=messageInfo["message"],
                                                                  date=datetime.utcfromtimestamp(
                                                                      messageInfo["date"]).strftime(
                                                                      '%Y-%m-%d %H:%M:%S'))
        mes += "Сообщение от " + ("пользователя с заказом" if messageInfo["isOrder"] else "обычного пользователя")
        mes += "\n<b>На сообщение уже ответили</b>" if not messageInfo["active"] else ""
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["usend", "usersend", "sendu", "usenduser"])
async def start_message_send(message: types.Message, state: FSMContext):
    mes = config.adminMessage["message_missing"]
    messageInfo = messagesModel.get_message(checkID(message.text))
    if messageInfo["success"] and not messageInfo["active"]:
        mes = config.adminMessage["order_completed"]
    elif messageInfo["success"]:
        async with state.proxy() as data:
            data["message_sendID"] = messageInfo["id"]
        await AdminMesUser.message.set()
        mes = config.adminMessage["message_send"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=AdminMesUser.message, user_id=config.ADMINS)
async def adding_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mes = data.get("message") if "message" in data.keys() else ""
    async with state.proxy() as data:
        data["message"] = mes + message.text + "\n"
    await message.answer(message.text + "\nПодтверждаете?",
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить"))
    await AdminMesUser.wait.set()


@dp.message_handler(state=AdminMesUser.wait)
async def waiting(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesUser.wait)
async def adding_message_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = config.adminMessage["message_completed"]
    data = await state.get_data()
    messageInfo = messagesModel.get_message(data.get("message_sendID"))
    text = data.get("message") if "message" in data.keys() else ""
    if messageInfo["success"] and messageInfo["active"]:
        await bot.send_message(chat_id=messageInfo["userID"], text=text, reply_markup=menu)
        messagesModel.updateActive_message(data.get("message_sendID"))
        mes = config.adminMessage["message_yes_send"]
    await call.message.edit_text(mes)
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesUser.wait)
async def adding_message_no(call: types.CallbackQuery):
    await call.message.edit_text(config.message["message_no"])
    await AdminMesUser.message.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminMesUser.wait)
async def adding_message_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["message_cancel"])
    await state.finish()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
