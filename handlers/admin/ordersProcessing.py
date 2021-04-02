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
from states.admin_close_order_pr import AdminCloseOrderPr
from states.admin_pr_mes import AdminPrMes
from states.admin_price_order import AdminPriceOrder
from utils.db_api.models import ordersProcessingModel, paymentModel
from utils import function


@dp.message_handler(Text(equals=["Заказы на рассмотрении", "/orderspr"]), user_id=config.ADMINS)
async def show_orders(message: types.Message):
    mes, keyboard = await menu_main(0)
    await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(numbering_callback.filter(what_action="OrderProcessingNumbering"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, callback_data: dict):
    mes, keyboard = await menu_main(int(callback_data["number"]))
    try:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    except:
        await call.answer(cache_time=1)


@dp.message_handler(user_id=config.ADMINS, commands=["infopr"])
async def show_info_order(message: types.Message):
    await menu_info_order(function.checkID(message.text), message)


@dp.message_handler(user_id=config.ADMINS, commands=["sendr"])
async def send_order_mes(message: types.Message, state: FSMContext):
    await menu_send_order(function.checkID(message.text), message, state)


@dp.callback_query_handler(action_callback.filter(what_action="OrderProcessingSend"), user_id=config.ADMINS)
async def send_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await menu_send_order(callback_data.get("id"), call.message, state)
    await call.message.delete()


@dp.message_handler(state=AdminPriceOrder.price, user_id=config.ADMINS)
async def send_order_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=message.text)
        await AdminPriceOrder.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["price_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы ввели не число")


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminPriceOrder.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = "Все пропало ((("
    data = await state.get_data()
    order = ordersProcessingModel.get_order_provisional(data.get("orderID"))
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        secret_key = hashlib.md5("{nameProduct}{time}".format(nameProduct="Работа на заказ", time=time.time()).encode())
        amount = order.calculate_price(int(data.get("price"))*100, secret_key.hexdigest())
        if amount < 100:
            await state.finish()
            await call.message.edit_text("Вышла сумма меньше 100р.\nОтправка отменена")
            return
        PRICE = types.LabeledPrice(label="Работа на заказ",
                                   amount=amount)
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
        order.set_state_wait()
        mes = config.adminMessage["message_yes_send"]
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminPriceOrder.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminPriceOrder)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


# Отказать в заказе #

@dp.message_handler(user_id=config.ADMINS, commands=["closer"])
async def close_order_mes(message: types.Message, state: FSMContext):
    await menu_close_order(function.checkID(message.text), message, state)


@dp.callback_query_handler(action_callback.filter(what_action="OrderProcessingCloser"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await menu_close_order(callback_data.get("id"), call.message, state)
    await call.message.delete()


@dp.message_handler(state=AdminCloseOrderPr.message, user_id=config.ADMINS)
async def close_order_text(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(text=message.text)
    await AdminCloseOrderPr.wait.set()
    await message.answer(config.adminMessage["order_close_confirm"], reply_markup=await buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminCloseOrderPr.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    mes = config.adminMessage["order_missing"]
    data = await state.get_data()
    order = ordersProcessingModel.get_order_provisional(data.get("orderID"))
    if order:
        text = config.message["orderPR_denied"]
        text += data.get("text")
        order.updateActive_order()
        await bot.send_message(chat_id=order.userID, text=text)
        await menu_info_order(order.id, call.message)
        mes = config.adminMessage["message_yes_send"]
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminCloseOrderPr.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(config.adminMessage["message_not_send"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminCloseOrderPr)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


# отправка сообщений пользователю #

@dp.callback_query_handler(action_callback.filter(what_action="OrderProcMessageSend"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(orderID=callback_data.get("id"))
    await AdminPrMes.message.set()
    mes = config.adminMessage["message_send"]
    keyboard = await buttons.getCustomKeyboard(cancel="Отмена")
    await call.message.answer(text=mes, reply_markup=keyboard)
    await call.message.delete()


@dp.message_handler(state=AdminPrMes.message, user_id=config.ADMINS)
async def close_order_text(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(text=message.text)
    await AdminPrMes.wait.set()
    await message.answer(config.message["comment_confirmation"].format(text=message.text), reply_markup=await buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=AdminPrMes.wait)
async def message_send_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    mes = config.adminMessage["order_missing"]
    data = await state.get_data()
    order = ordersProcessingModel.get_order_provisional(data.get("orderID"))
    if order:
        text = config.adminMessage["order_send_mes"].format(orderID=order.id)
        text += data.get("text")
        await bot.send_message(chat_id=order.userID, text=text)
        await menu_info_order(order.id, call.message)
        mes = config.adminMessage["message_yes_send"]
    await state.finish()
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=AdminPrMes.wait)
async def message_send_no(call: types.CallbackQuery, state: FSMContext):
    await AdminPrMes.message.set()
    await call.message.edit_text(text=config.adminMessage["message_send"], reply_markup=await buttons.getCustomKeyboard(cancel="Отмена"))


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=AdminPrMes)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await menu_info_order(data.get("orderID"), call.message)
    await state.finish()


async def menu_send_order(orderID, message, state):
    mes = config.adminMessage["order_missing"]
    keyboard = None
    order = ordersProcessingModel.get_order_provisional(orderID)
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        await state.update_data(message_sendID=order.userID, orderID=order.id)
        await AdminPriceOrder.price.set()
        mes = config.adminMessage["price_send"]
        keyboard = await buttons.getCustomKeyboard(cancel="Отмена")
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_close_order(orderID, message, state):
    mes = config.adminMessage["order_missing"]
    keyboard = None
    order = ordersProcessingModel.get_order_provisional(orderID)
    if order and not order.active:
        mes = config.adminMessage["order_completed"]
    elif order:
        await state.update_data(orderID=order.id)
        await AdminCloseOrderPr.message.set()
        mes = config.adminMessage["order_close_text"]
        keyboard = await buttons.getCustomKeyboard(cancel="Отмена")
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_info_order(orderID, message):
    mes = config.adminMessage["order_missing"]
    keyboard = None
    order = ordersProcessingModel.get_order_provisional(orderID)
    if order:
        mes = config.adminMessage["order_pr_detailed_info"].format(orderID=order.id, userID=order.userID,
                                                                   text=order.text,
                                                                   discount=order.promoCodeInfo,
                                                                   payment=order.otherDiscount,
                                                                   date=time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                      time.localtime(order.date)))
        mes += "" if order.active else "<b>Заказ рассмотрен</b>"
        keyboard = await buttons.getActionKeyboard(order.id, OrderProcessingSend="Отправить форму оплаты", OrderProcMessageSend="Написать",
                                                   OrderProcessingCloser="Отказать") if order.active else None
        if order.document:
            await message.answer_document(caption=mes, document=order.document, reply_markup=keyboard)
            return
    await message.answer(text=mes, reply_markup=keyboard)


async def menu_main(page):
    orders = ordersProcessingModel.get_orders_provisional(page, config.max_size_order_provisional)
    orders_count = ordersProcessingModel.get_ALLOrders_provisional_count()
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
            text += config.adminMessage["order_info"].format(num=num + (page * config.max_size_order_provisional),
                                                             orderID=item.id, date=dateMes)
            num += 1
        mes = config.adminMessage["ordersPR_main"].format(text=text)
        keyboard = await buttons.getNumbering(math.ceil(orders_count / config.max_size_order_provisional),
                                              "OrderProcessingNumbering")
    else:
        mes = config.adminMessage["orders_missing"]
    return mes, keyboard
