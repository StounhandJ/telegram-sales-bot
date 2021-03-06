import hashlib
import math
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback, numbering_callback
from loader import dp, bot
from states.admin_close_order import AdminCloseOrder
from states.admin_mes_order import AdminMesOrder
from utils.db_api.models import orderModel, tasksModel, paymentModel
from utils import function


### Информация о заказах ###
from utils.telegram_files import TelegramFiles


@dp.message_handler(Text(equals=["Заказы", "/orders"]), user_id=config.ADMINS)
async def show_orders(message: types.Message):
    mes, keyboard = await menu_main(0)
    await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(numbering_callback.filter(what_action="OrderNumbering"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, callback_data: dict):
    mes, keyboard = await menu_main(int(callback_data["number"]))
    try:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    except:
        await call.answer(cache_time=1)


@dp.message_handler(user_id=config.ADMINS, commands=["info"])
async def show_info_order(message: types.Message):
    await menu_info_order(function.checkID(message.text), message)


@dp.message_handler(user_id=config.ADMINS, commands=["orderClose"])
async def close_order(message: types.Message, state: FSMContext):
    await menu_close_order(function.checkID(message.text), message, state)


@dp.callback_query_handler(action_callback.filter(what_action="OrderClose"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await menu_close_order(callback_data.get("id"), call.message, state)
    await call.message.delete()


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminCloseOrder.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    data = await state.get_data()
    order = orderModel.get_order(data.get("orderID"))
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        order.updateActive_order()
        tasksModel.del_task_orderID(order.id)
        mes = config.adminMessage["order_close"].format(id=order.id)
        await bot.send_message(chat_id=order.userID, text=config.message["order_close"])
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminCloseOrder.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


### Отправка соощения по заказу ###

@dp.message_handler(user_id=config.ADMINS, commands=["send"])
async def start_message_send(message: types.Message, state: FSMContext):
    await menu_send_order(function.checkID(message.text), message, state)


@dp.callback_query_handler(action_callback.filter(what_action="OrderSend"), user_id=config.ADMINS)
async def send_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await menu_send_order(callback_data.get("id"), call.message, state)
    await call.message.delete()


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
        DocMes += "{name} {size}мб\n".format(name=item.file_name, size=round(item.file_size/1024/1024, 3))
    for item in img:
        ImgMes += "{height}x{width} {size}мб\n".format(height=item.height,
                                                       width=item.width,
                                                       size=round(item.file_size/1024/1024, 3))
    ResponseMes = "<b>Текст</b>:\n{text}\n <b>Документы</b>:\n{doc}\n <b>Изображения</b>:\n {img}".format(text=mes,
                                                                                                          doc=DocMes,
                                                                                                          img=ImgMes)
    await message.answer(ResponseMes)


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    if TelegramFiles.document_size(message.document.file_size):
        data = await state.get_data()
        keys = data.keys()
        mes = data.get("description") if "description" in keys else ""
        doc = data.get("document") if "document" in keys else []
        async with state.proxy() as data:
            doc.append(message.document)
            data["document"] = doc
            data["description"] = mes + (message.caption + "\n" if message.caption is not None else "")
        await message.answer(
            config.adminMessage["document_add"] + "\n" + config.adminMessage["message_send_confirmation"],
            reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer(config.message["document_confirmation_size"].format(
            text="{name} {size}мб\n".format(name=message.document.file_name, size=round(message.document.file_size/1024/1024, 3))),
            reply_markup=await buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS, content_types=types.ContentType.PHOTO)
async def message_add_img(message: types.Message, state: FSMContext):
    if TelegramFiles.photo_size(message.photo[0].file_size) and TelegramFiles.image_aspect_ratio(message.photo[0].width,message.photo[0].height):
        data = await state.get_data()
        keys = data.keys()
        mes = data.get("description") if "description" in keys else ""
        img = data.get("img") if "img" in keys else []
        async with state.proxy() as data:
            img.append(message.photo[0])
            data["img"] = img
            data["description"] = mes + (message.caption + "\n" if message.caption is not None else "")
        await message.answer(config.adminMessage["img_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer(config.message["img_no"])


@dp.message_handler(state=AdminMesOrder.message, user_id=config.ADMINS)
async def message_add_mes(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    data = await state.get_data()
    mes = data.get("description") if "description" in data.keys() else ""
    await state.update_data(description=(mes + message.text + "\n"))
    await message.answer(config.adminMessage["mes_add"] + "\n" + config.adminMessage["message_send_confirmation"],
                         reply_markup=await buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminMesOrder.message)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    order = orderModel.get_order(data.get("orderID"))
    if not order or (order and not order.active):
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
        await bot.send_photo(chat_id=chatID, photo=item.file_id)
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_yes_send"])


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminMesOrder.message)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_not_send"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminMesOrder)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


# Повторная оплата #

@dp.callback_query_handler(action_callback.filter(what_action="OrderPaymentTwo"), user_id=config.ADMINS)
async def send_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(callback_data.get("id"))
    keyboard = None
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        PRICE = types.LabeledPrice(label="Работа на заказ",
                                   amount=int(order.price / 2) * 100)
        secret_key = hashlib.md5("{nameProduct}{time}".format(nameProduct="Работа на заказ", time=time.time()).encode())
        await bot.send_message(order.userID, config.payMessage["payment_two"])
        await bot.send_invoice(
            chat_id=order.userID,
            title=config.payMessage["title"],
            description=config.payMessage["description"],
            provider_token=config.PAYMENT_TOKEN,
            currency=config.currency,
            is_flexible=False,
            prices=[PRICE],
            start_parameter='time-machine-example',
            payload=secret_key.hexdigest()
        )
        order.set_paymentKey_order(secret_key.hexdigest())
        paymentModel.create_payment(call.from_user.id, order.description, order.document,
                                    order.separate_payment,
                                    order.price / 2,
                                    secret_key.hexdigest(), True)
        mes = "Отправленно"
    await call.message.answer(mes)
    await menu_info_order(callback_data.get("id"), call.message)
    await call.message.delete()


async def menu_send_order(orderID, message, state):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(orderID)
    keyboard = None
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        await state.update_data(message_sendID=order.userID, orderID=order.id)
        await AdminMesOrder.message.set()
        mes = config.adminMessage["message_send"]
        keyboard = await buttons.getCustomKeyboard(cancel="Отмена")
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_close_order(orderID, message, state):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(orderID)
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        mes = config.adminMessage["order_confirm"]
        await state.update_data(orderID=order.id)
        await AdminCloseOrder.wait.set()
    await message.answer(mes, reply_markup=await buttons.getConfirmationKeyboard())


async def menu_info_order(orderID, message):
    mes = config.adminMessage["order_missing"]
    order = orderModel.get_order(orderID)
    keyboard = None
    if order:
        payment = paymentModel.get_payment(order.payment_key)
        mes = config.adminMessage["order_detailed_info"].format(orderID=order.id,
                                                                price=order.price,
                                                                description=order.description,
                                                                payment="половина суммы" if order.separate_payment else "вся сумма",
                                                                date=time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                   time.localtime(order.date)))
        mes += "" if order.active else "<b>Заказ выполнен</b>"
        mes += "<b>Ожидает оплаты второй части</b>" if payment else ""
        if order.active and order.separate_payment and not payment:
            keyboard = await buttons.getActionKeyboard(order.id, OrderSend="Отправить ответ",
                                                       OrderClose="Закрыть заказ",
                                                       OrderPaymentTwo="Отправить вторую оплату")
        elif order.active:
            keyboard = await buttons.getActionKeyboard(order.id, OrderSend="Отправить ответ",
                                                       OrderClose="Закрыть заказ")
        if len(order.document) == 1:
            await message.answer_document(caption=mes, document=order.document[0], reply_markup=keyboard)
            return
        elif len(order.document) > 1:
            for document in order.document:
                await message.answer_document(document=document)
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_main(page):
    orders = orderModel.get_orders(page, config.max_size_order)
    orders_count = orderModel.get_ALLOrders_count()
    keyboard = None
    if orders:
        text = ""
        num = 1
        for item in orders:
            date = time.localtime(item.date)
            dateMes = "{year} год {day} {month} {min}".format(year=date.tm_year, day=date.tm_mday,
                                                              month=config.months[date.tm_mon - 1],
                                                              hour=date.tm_hour,
                                                              min=time.strftime("%H:%M", date))
            text += config.adminMessage["order_info"].format(num=num + (page * config.max_size_order),
                                                             orderID=item.id, date=dateMes)
            num += 1
        mes = config.adminMessage["orders_main"].format(text=text)
        keyboard = await buttons.getNumbering(math.ceil(orders_count / config.max_size_order), "OrderNumbering")
    else:
        mes = config.adminMessage["orders_missing"]
    return mes, keyboard
