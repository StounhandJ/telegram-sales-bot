import hashlib
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp, bot
from states.admin_close_order_pr import AdminCloseOrderPr
from states.admin_price_order import AdminPriceOrder
from utils.db_api.models import ordersProcessingModel, paymentModel


@dp.message_handler(user_id=config.ADMINS, commands=["orderspr"])
async def show_orders(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    orders = ordersProcessingModel.get_ALLOrders_provisional()
    if orders["success"]:
        text = ""
        num = 1
        for item in orders["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            text += config.adminMessage["order_info"].format(num=num, orderID=item["id"], date=dateMes)
            num += 1
        mes = config.adminMessage["ordersPR_main"].format(text=text)
    else:
        mes = config.adminMessage["orders_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["infopr"])
async def show_info_order(message: types.Message):
    mes = config.adminMessage["order_missing"]
    order = ordersProcessingModel.get_order_provisional(checkID(message.text))
    if order["success"]:
        mes = config.adminMessage["order_pr_detailed_info"].format(orderID=order["id"], text=order["text"],
                                                                   discount=str(order["discount"]) + (
                                                                       "%" if order["percent"] else " р."),
                                                                   date=datetime.utcfromtimestamp(
                                                                       order["date"]).strftime('%Y-%m-%d %H:%M:%S'))
        mes += "<b>Заказ выполнен</b>" if not order["active"] else ""
        if len(order["document"]) == 1:
            await message.answer_document(caption=mes, document=order["document"][0])
            return
        elif len(order["document"]) > 1:
            for document in order["document"]:
                await message.answer_document(document=document)
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["sendr"])
async def send_order(message: types.Message, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    order = ordersProcessingModel.get_order_provisional(checkID(message.text))
    if order["success"] and not order["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["success"]:
        async with state.proxy() as data:
            data["message_sendID"] = order["userID"]
            data["orderID"] = order["id"]
        await AdminPriceOrder.price.set()
        mes = config.adminMessage["price_send"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["closer"])
async def close_order(message: types.Message, state: FSMContext):
    mes = config.adminMessage["order_missing"]
    order = ordersProcessingModel.get_order_provisional(checkID(message.text))
    if order["success"]:
        mes = config.adminMessage["order_close_text"]
        async with state.proxy() as data:
            data["orderID"] = order["id"]
        await AdminCloseOrderPr.message.set()
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=AdminCloseOrderPr.message, user_id=config.ADMINS)
async def close_order_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["text"] = message.text
    await AdminCloseOrderPr.wait.set()
    await message.answer(config.adminMessage["order_close_confirm"], reply_markup=buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminCloseOrderPr.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = config.adminMessage["order_missing"]
    data = await state.get_data()
    order = ordersProcessingModel.get_order_provisional(data.get("orderID"))
    if order["success"]:
        mes = config.adminMessage["message_yes_send"]
        await bot.send_message(chat_id=order["userID"], text=data.get("text"))
        ordersProcessingModel.updateActive_order(data.get("orderID"))
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminCloseOrderPr.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["message_not_send"])
    await state.finish()


@dp.message_handler(state=AdminPriceOrder.price, user_id=config.ADMINS)
async def send_order_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data["price"] = message.text
        await AdminPriceOrder.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["price_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы ввели не число")


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminPriceOrder.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = "Все пропало ((("
    data = await state.get_data()
    order = ordersProcessingModel.get_order_provisional(data.get("orderID"))
    if order["success"] and not order["active"]:
        mes = config.adminMessage["order_completed"]
    elif order["success"]:
        amount = int(data.get("price")) - (
            int(data.get("price")) / 100 * order["discount"] if order["percent"] and order["discount"] != 0 else order[
                "discount"])
        amount = int(amount)
        PRICE = types.LabeledPrice(label="Работа на заказ", amount=amount * 100)
        secret_key = hashlib.md5("{nameProduct}{time}".format(nameProduct="Работа на заказ", time=time.time()).encode())
        await bot.send_invoice(
            call.from_user.id,
            title=config.payMessage["title"],
            description=config.payMessage["description"],
            provider_token=config.PAYMENT_TOKEN,
            currency=config.currency,
            is_flexible=False,
            prices=[PRICE],
            start_parameter='time-machine-example',
            payload=secret_key.hexdigest()
        )
        paymentModel.del_payment(call.from_user.id)
        paymentModel.create_payment(call.from_user.id, "Работа на заказ", order["text"], amount,
                                    secret_key.hexdigest())
        ordersProcessingModel.updateActive_order(data.get("orderID"))
        mes = config.adminMessage["message_yes_send"]
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminPriceOrder.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["message_not_send"])
    await state.finish()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
