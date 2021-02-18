from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp, bot
from states.admin_close_order import AdminCloseOrder
from states.admin_mes_order import AdminMesOrder
from utils.db_api.models import orderModel, tasksModel
from utils import function


### Информация о заказах ###

@dp.message_handler(Text(equals=["Заказы"]), user_id=config.ADMINS)
async def show_orders(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    orders = orderModel.get_ALLOrders()
    if orders["code"] == 200:
        text = ""
        num = 1
        for item in orders["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            text += config.adminMessage["order_info"].format(num=num, orderID=item["id"], date=dateMes)
            num += 1
        mes = config.adminMessage["orders_main"].format(text=text)
    else:
        mes = config.adminMessage["orders_missing"]
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["info"])
async def show_info_order(message: types.Message):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(function.checkID(message.text))
    if order["code"] == 200:
        order = order["data"]
        mes = config.adminMessage["order_detailed_info"].format(orderID=order["id"],
                                                                price=order["price"],
                                                                description=order["description"],
                                                                date=datetime.utcfromtimestamp(
                                                                    order["date"]).strftime('%Y-%m-%d %H:%M:%S'))
        mes += "<b>Заказ выполнен</b>" if not order["active"] else ""
        if len(order["document"]) == 1:
            await message.answer_document(caption=mes, document=order["document"][0])
            return
        elif len(order["document"]) > 1:
            for document in order["document"]:
                await message.answer_document(document=document)
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["orderClose"])
async def close_order(message: types.Message, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(function.checkID(message.text))
    if order["code"] == 200 and not order["data"]["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["code"] == 200:
        mes = config.adminMessage["order_confirm"]
        await state.update_data(orderID=order["data"]["id"])
        await AdminCloseOrder.wait.set()
    await message.answer(mes, reply_markup=buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminCloseOrder.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    data = await state.get_data()
    order = orderModel.get_order(data.get("orderID"))
    if order["code"] == 200 and not order["data"]["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["code"] == 200:
        orderModel.updateActive_order(order["data"]["id"])
        tasksModel.del_task_orderID(order["data"]["id"])
        mes = config.adminMessage["order_close"].format(id=order["data"]["id"])
        await bot.send_message(chat_id=order["data"]["userID"], text=config.message["order_close"])
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminCloseOrder.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["order_confirm_no"])
    await state.finish()


### Отправка соощения по заказу ###

@dp.message_handler(user_id=config.ADMINS, commands=["send"])
async def start_message_send(message: types.Message, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(function.checkID(message.text))
    if order["code"] == 200 and not order["data"]["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["code"] == 200:
        await state.update_data(message_sendID=order["data"]["userID"])
        await state.update_data(orderID=order["data"]["id"])
        await AdminMesOrder.message.set()
        mes = config.adminMessage["message_send"]
    await message.answer(mes)


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, commands=["mesCheck"])
async def message_check(message: types.Message, state: FSMContext):
    DocMes = ""
    ImgMes = ""
    data = await state.get_data()
    keys = data.keys()
    mes = data.get("description") if "description" in keys else ""
    doc = data.get("document") if "document" in keys else []
    img = data.get("img") if "img" in keys else []
    for item in doc:
        DocMes += "{name} {size}кб\n".format(name=item.file_name, size=item.file_size)
    for item in img:
        ImgMes += "{height}x{width} {size}кб\n".format(height=item[len(item) - 1].height,
                                                       width=item[len(item) - 1].width,
                                                       size=item[len(item) - 1].file_size)
    ResponseMes = "<b>Текст</b>:\n{text}\n <b>Документы</b>:\n{doc}\n <b>Изображения</b>:\n {img}".format(text=mes,
                                                                                                          doc=DocMes,
                                                                                                          img=ImgMes)
    await message.answer(ResponseMes)


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    mes = data.get("description") if "description" in keys else ""
    doc = data.get("document") if "document" in keys else []
    async with state.proxy() as data:
        doc.append(message.document)
        data["document"] = doc
        data["description"] = mes + (message.caption + "\n" if message.caption is not None else "")
    await message.answer(config.adminMessage["document_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, content_types=types.ContentType.PHOTO)
async def message_add_img(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    mes = data.get("description") if "description" in keys else ""
    img = data.get("img") if "img" in keys else []
    async with state.proxy() as data:
        img.append(message.photo)
        data["img"] = img
        data["description"] = mes + (message.caption + "\n" if message.caption is not None else "")
    await message.answer(config.adminMessage["img_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS)
async def message_add_mes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mes = data.get("description") if "description" in data.keys() else ""
    await state.update_data(description=(mes + message.text + "\n"))
    await message.answer(config.adminMessage["mes_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesOrder.message)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    order = orderModel.get_order(data.get("orderID"))
    if not order["code"] == 200 or (order["code"] == 200 and not order["data"]["active"]):
        await state.finish()
        await call.message.edit_text(config.adminMessage["order_completed"])
        return
    keys = data.keys()
    chatID = data.get("message_sendID")
    mes = data.get("description") if "description" in keys else ""
    doc = data.get("document") if "document" in keys else []
    img = data.get("img") if "img" in keys else []
    await bot.send_message(chat_id=chatID, text=config.message["order_complete"])
    if len(doc) == 0 and mes != "":
        await bot.send_message(chat_id=chatID, text=mes)
    elif len(doc) == 1:
        await bot.send_document(chat_id=chatID, caption=mes, document=doc[0].file_id)
    elif len(doc) > 1:
        for document in doc:
            await bot.send_document(chat_id=chatID, document=document.file_id)
        if mes != "":
            await bot.send_message(chat_id=chatID, text=mes)
    for item in img:
        await bot.send_photo(chat_id=chatID, photo=item[len(item) - 1].file_id)
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_yes_send"])


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesOrder.message)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_not_send"])
