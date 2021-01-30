from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, CommandStart
from data import config
from utils.db_api import models
from keyboards.default import menu
from loader import dp
from datetime import datetime


@dp.message_handler(user_id=config.ADMINS, commands=["orders"])
async def show_menu(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    orders = models.get_ALLOrders()
    if orders["success"]:
        mes = config.adminMessage["order_main"]
        num = 1
        for item in orders["data"]:
            date = datetime.utcfromtimestamp(item["date"])
            dateMes = "{year} год {day} {month} {min}".format(year=date.year, day=date.day,
                                                              month=months[date.month - 1],
                                                              min=date.strftime("%H:%M"))
            mes += config.adminMessage["order_info"].format(num=num, orderID=item["id"], date=dateMes)
            num += 1
    else:
        mes = config.adminMessage["order_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["info"])
async def show_menu(message: types.Message):
    mes = "Данный заказ не найден"
    order = models.get_order(int(message.text.split(' ')[1]))
    if order["success"]:
        product = models.get_product(order["productID"])
        productName = product["name"] if product["success"] else "Товар удален"
        productPrice = product["price"] if product["success"] else "Товар удален"
        mes = config.adminMessage["order_detailed_info"].format(orderID=order["id"], product=productName,
                                                                price=productPrice,
                                                                description=order["description"],
                                                                date=datetime.utcfromtimestamp(
                                                                    order["date"]).strftime('%Y-%m-%d %H:%M:%S'))

    await message.answer(mes, reply_markup=menu)
