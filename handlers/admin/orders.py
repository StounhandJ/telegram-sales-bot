from aiogram import types
from aiogram.dispatcher import FSMContext
from data import config
from datetime import datetime
from states.admin_mes_order import AdminMesOrder
from keyboards.inline import choice_buttons
from keyboards.inline.callback_datas import confirmation_callback
from keyboards.default import menu
from loader import dp, bot
from utils.db_api import models


### Информация о заказах ###

@dp.message_handler(user_id=config.ADMINS, commands=["orders"])
async def show_orders(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    orders = models.get_ALLOrders()
    if orders["success"]:
        mes = config.adminMessage["orders_main"]
        num = 1
        for item in orders["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            mes += config.adminMessage["order_info"].format(num=num, orderID=item["id"], date=dateMes)
            num += 1
    else:
        mes = config.adminMessage["orders_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["info"])
async def show_info_order(message: types.Message):
    mes = "Данный заказ не найден"
    order = models.get_order(checkID(message.text))
    if order["success"]:
        productName = order["nameProduct"]
        productPrice = order["price"]
        mes = config.adminMessage["order_detailed_info"].format(orderID=order["id"], product=productName,
                                                                price=productPrice,
                                                                description=order["description"],
                                                                date=datetime.utcfromtimestamp(
                                                                    order["date"]).strftime('%Y-%m-%d %H:%M:%S'))
        mes += "<b>Заказ выполнен</b>" if not order["active"] else ""
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["orderClose"])
async def message_order_close(message: types.Message):
    mes = config.adminMessage["order_missing"]
    order = models.get_order(checkID(message.text))
    if order["success"] and not order["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["success"]:
        models.updateActive_order(order["id"])
        mes = config.adminMessage["order_close"].format(id=order["id"])

    await message.answer(mes, reply_markup=menu)


### Отправка соощения по заказу ###

@dp.message_handler(user_id=config.ADMINS, commands=["send"])
async def message_send_start(message: types.Message, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    order = models.get_order(checkID(message.text))
    if order["success"] and not order["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["success"]:
        async with state.proxy() as data:
            data["message_sendID"] = order["userID"]
            data["orderID"] = order["id"]
        await AdminMesOrder.message.set()
        mes = config.adminMessage["message_send"]

    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, commands=["mesCheck"])
async def message_handler(message: types.Message, state: FSMContext):
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
    await message.answer(ResponseMes, reply_markup=menu)


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
                         reply_markup=choice_buttons.getConfirmationKeyboard())


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
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS)
async def message_add_mes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mes = data.get("description") if "description" in data.keys() else ""
    async with state.proxy() as data:
        data["description"] = mes + message.text + "\n"
    await message.answer(config.adminMessage["mes_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesOrder.message)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    order = models.get_order(data.get("orderID"))
    if not order["success"] or (order["success"] and not order["active"]):
        await call.message.edit_text(config.adminMessage["order_completed"])
        await AdminMesOrder.next()
        await state.finish()
        return
    keys = data.keys()
    chatID = data.get("message_sendID")
    mes = data.get("description") if "description" in keys else ""
    doc = data.get("document") if "document" in keys else []
    img = data.get("img") if "img" in keys else []
    if mes != "":
        await bot.send_message(chat_id=chatID, text=mes, reply_markup=menu)
    for item in doc:
        await bot.send_document(chat_id=chatID, document=item.file_id, reply_markup=menu)
    for item in img:
        await bot.send_photo(chat_id=chatID, photo=item[len(item) - 1].file_id, reply_markup=menu)
    await AdminMesOrder.next()
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_yes_send"])


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesOrder.message)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["document"] = ""
        data["description"] = ""
    await call.message.edit_text(config.adminMessage["message_not_send"])
    await AdminMesOrder.next()
    await state.finish()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
