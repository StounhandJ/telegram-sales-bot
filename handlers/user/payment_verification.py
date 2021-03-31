import time

from aiogram import types

from data import config
from loader import dp, bot
from utils.db_api.models import paymentModel, orderModel, userModel
from utils.notify_admins import notify_admins_message


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    payment = paymentModel.get_payment(pre_checkout_query.invoice_payload)
    await bot.answer_pre_checkout_query(pre_checkout_query.id,
                                        ok=payment and payment.date + 60 * 60 * 24 * 30 > time.time(),
                                        error_message=config.errorMessage["exceeded_time_pay"])
    if payment and not (payment.date + 60 * 60 * 24 * 30 > time.time()):
        payment.del_payment()


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    paymentModel.add_payment_history(message.from_user.id, message.successful_payment.total_amount // 100)
    userModel.update_payment(message.from_user.id, message.successful_payment.total_amount // 100)
    mes = config.errorMessage["payment_missing"]
    payment = paymentModel.get_payment(message.successful_payment.invoice_payload)
    if payment:
        mes_admin = "Тут прилители халявные деньги\nТак то приятно)\nНо надо бы разобраться что случилось"
        if payment.additional:
            order = orderModel.get_order_paymentKey(payment.secret_key)
            if order:
                order.del_Separate_order()
                mes_admin = config.adminMessage["admin_mes_order_paid_two"].format(orderID=order.id)
        else:
            orderModel.create_order(message.from_user.id, payment.description, payment.document,
                                    payment.price, payment.separate_payment)
            mes_admin = config.adminMessage["admin_mes_order_paid"]
        payment.del_payment()
        mes = config.message["comment_confirmation_yes"]
        await notify_admins_message(mes_admin)
    await message.answer(mes)
