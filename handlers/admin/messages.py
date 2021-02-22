from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback
from loader import dp, bot
from states.admin_mes_user import AdminMesUser
from utils.db_api.models import messagesModel
from utils import function


@dp.message_handler(Text(equals=["Сообщения от заказчиков", "/mesOrder"]), user_id=config.ADMINS)
async def order_messages(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    messages = messagesModel.get_order_messages()
    if messages["code"] == 200:
        start = config.adminMessage["messages_main_order"]
        text = ""
        num = 1
        for item in messages["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            text += config.adminMessage["messages_info"].format(num=num, id=item["id"], date=dateMes)
            num += 1
        mes = config.adminMessage["messages_main"].format(start=start, text=text)
    else:
        mes = config.adminMessage["messages_missing"]
    await message.answer(mes)


@dp.message_handler(Text(equals=["Сообщения от пользователей", "/mesUser"]), user_id=config.ADMINS)
async def all_messages(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    messages = messagesModel.get_all_messages()
    if messages["code"] == 200:
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
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["mesinfo", "infomes"])
async def show_info_mes(message: types.Message):
    await menu_info_mes(function.checkID(message.text), message)


# Отправка сообщения #

@dp.message_handler(user_id=config.ADMINS, commands=["usend", "usersend", "sendu", "usenduser"])
async def start_message_send(message: types.Message, state: FSMContext):
    await menu_send_mes(function.checkID(message.text), message, state)


@dp.callback_query_handler(action_callback.filter(what_action="MessageSend"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await menu_send_mes(callback_data.get("id"), call.message, state)
    await call.message.delete()


@dp.message_handler(state=AdminMesUser.message)
async def adding_comment(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(message=message.text)
    await AdminMesUser.wait.set()
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить"))


@dp.message_handler(state=AdminMesUser.wait)
async def waiting(message: types.Message):
    pass


@dp.message_handler(state=AdminMesUser.document, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document)
    await AdminMesUser.wait.set()
    await message.answer(config.message["document_confirmation"].format(
        text="{name} {size}кб\n".format(name=message.document.file_name, size=message.document.file_size)),
        reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить"))


@dp.message_handler(state=AdminMesUser.document, content_types=types.ContentType.PHOTO)
async def message_add_doc(message: types.Message):
    await message.answer(text=config.errorMessage["not_add_photo"])


@dp.callback_query_handler(confirmation_callback.filter(bool="noElement"), state=AdminMesUser)
async def adding_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = ""
    state_active = data.get("state_active")
    keyboard = None
    if "AdminMesUser:document" == state_active:
        await send_mes(call, state)
        return
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesUser)
async def adding_comment_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = ""
    keyboard = None
    if "AdminMesUser:document" == state_active:
        await send_mes(call, state)
        return
    elif "AdminMesUser:documentCheck" == state_active:
        await AdminMesUser.document.set()
        mes = config.message["comment_document"]
        keyboard = buttons.getCustomKeyboard(noElement="Нет файла")
    elif "AdminMesUser:message" == state_active:
        await AdminMesUser.documentCheck.set()
        mes = config.message["comment_documentCheck"]
        keyboard = buttons.getConfirmationKeyboard(cancel="Отменить")
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesUser)
async def adding_comment_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    keyboard = buttons.getCustomKeyboard(cancel="Отменить")
    if "AdminMesUser:document" == state_active:
        await AdminMesUser.document.set()
    elif "AdminMesUser:documentCheck" == state_active:
        await send_mes(call, state)
        return
    elif "AdminMesUser:message" == state_active:
        await AdminMesUser.message.set()

    await call.message.edit_text(text=config.message["message_no"], reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminMesUser)
async def adding_message_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_mes(data.get("message_sendID"), call.message)
    await state.finish()


async def send_mes(call, state):
    await call.answer(cache_time=2)
    data = await state.get_data()
    messageInfo = messagesModel.get_message(data.get("message_sendID"))
    if not messageInfo["code"] == 200 or (messageInfo["code"] == 200 and not messageInfo["data"]["active"]):
        await state.finish()
        await call.message.edit_text(config.adminMessage["order_completed"])
        return
    keys = data.keys()
    chatID = messageInfo["data"]["userID"]
    mes = data.get("message") if "message" in keys else ""
    doc = [data.get("document").file_id] if "document" in keys else []
    await bot.send_message(chat_id=chatID, text="<b>Ответ на вашу заявку</b>:")
    if len(doc) == 0 and mes != "":
        await bot.send_message(chat_id=chatID, text=mes)
    elif len(doc) == 1:
        await bot.send_document(chat_id=chatID, caption=mes, document=doc[0])
    elif len(doc) > 1:
        for document in doc:
            await bot.send_document(chat_id=chatID, document=document)
        if mes != "":
            await bot.send_message(chat_id=chatID, text=mes)
    messagesModel.updateActive_message(data.get("message_sendID"))
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_yes_send"])


async def menu_send_mes(mesID, message, state):
    mes = config.adminMessage["message_missing"]
    messageInfo = messagesModel.get_message(mesID)
    keyboard = None
    if messageInfo["code"] == 200 and not messageInfo["data"]["active"]:
        mes = config.adminMessage["order_completed"]
    elif messageInfo["code"] == 200:
        await state.update_data(message_sendID=messageInfo["data"]["id"])
        await AdminMesUser.message.set()
        await function.set_state_active(state)
        mes = config.adminMessage["message_send"]
        keyboard = buttons.getCustomKeyboard(cancel="Отмена")
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_info_mes(mesID, message):
    mes = "Данное сообщние не найдено"
    messageInfo = messagesModel.get_message(mesID)
    keyboard = None
    if messageInfo["code"] == 200:
        messageInfo = messageInfo["data"]
        mes = config.adminMessage["message_detailed_info"].format(id=messageInfo["id"], userID=messageInfo["userID"], text=messageInfo["message"],
                                                                  date=datetime.utcfromtimestamp(
                                                                      messageInfo["date"]).strftime(
                                                                      '%Y-%m-%d %H:%M:%S'))
        mes += "Сообщение от " + ("пользователя с заказом" if messageInfo["isOrder"] else "обычного пользователя")
        mes += "" if messageInfo["active"] else "\n<b>На сообщение уже ответили</b>"
        keyboard = buttons.getActionKeyboard(messageInfo["id"], MessageSend="Ответить") if messageInfo[
            "active"] else None
        if len(messageInfo["document"]) == 1:
            await message.answer_document(caption=mes, document=messageInfo["document"][0], reply_markup=keyboard)
            return
        elif len(messageInfo["document"]) > 1:
            for document in messageInfo["document"]:
                await message.answer_document(document=document)
    await message.answer(text=mes, reply_markup=keyboard)
