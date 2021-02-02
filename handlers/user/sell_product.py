from textwrap import wrap
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback
from keyboards.inline import choice_buttons
from loader import dp, bot
from data import config
from utils.db_api import models
from states.sell_info import SellInfo
import time, hashlib


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    payment = models.get_payment(pre_checkout_query.from_user.id)
    await bot.answer_pre_checkout_query(pre_checkout_query.id,
                                        ok=payment["success"] and payment["date"] + 60 * 60 * 24 * 7 > time.time() and
                                           pre_checkout_query.invoice_payload == payment["secret_key"],
                                        error_message=config.errorMessage["exceeded_time_pay"])


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    models.add_payment_history(message.from_user.id, message.successful_payment.total_amount // 100)
    mes = config.errorMessage["payment_missing"]
    payment = models.get_payment(message.from_user.id)
    if payment["success"]:
        models.create_order(message.from_user.id, payment["description"], payment["nameProduct"],
                            message.successful_payment.total_amount // 100)
        mes = config.message["comment_confirmation_yes"]
    models.del_payment(message.from_user.id)
    await message.answer(mes)


@dp.callback_query_handler(buy_callback.filter())
async def product_info(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    async with state.proxy() as data:
        data["productID"] = callback_data["id"]
    product = models.get_product(callback_data["id"])
    if product["success"]:
        price = ""
        temporaryArrayNumbers = wrap(str(product["price"])[::-1], 3)
        temporaryArrayNumbers.reverse()
        for numbers in temporaryArrayNumbers:
            price += numbers[::-1] + " "
        await call.message.edit_text(
            text=config.message["product_info"].format(item_name=product["name"], price=price + "р.",
                                                       description=product["description"]),
            reply_markup=choice_buttons.getSellProductsKeyboard())
    else:
        await call.message.edit_text(config.errorMessage["product_missing"])


@dp.callback_query_handler(setting_callback.filter(command="exit"))
async def show_product(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=choice_buttons.getProductsKeyboard())
    await state.finish()


@dp.callback_query_handler(setting_callback.filter(command="add"))
async def comment_order(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_order"])
    await SellInfo.description.set()


@dp.message_handler(state=SellInfo.description)
async def comment_confirmation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=choice_buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
    await SellInfo.wait.set()


@dp.message_handler(state=SellInfo.wait)
async def comment_confirmation(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.wait)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    product = models.get_product(data.get("productID"))
    description = data.get("description") if "description" in data.keys() else ""
    if product["success"]:
        PRICE = types.LabeledPrice(label=product["name"], amount=product["price"] * 100)
        secret_key = hashlib.md5("{nameProduct}{time}".format(nameProduct=product["name"],time=time.time()).encode())
        await bot.send_invoice(
            call.from_user.id,
            title=config.payMessage["title"],
            description=product["description"],
            provider_token="401643678:TEST:f61b1a00-7bf2-4169-8b25-397bee1085d4",
            currency='rub',
            is_flexible=False,
            prices=[PRICE],
            start_parameter='time-machine-example',
            payload=secret_key.hexdigest()
        )
        models.del_payment(call.from_user.id)
        models.create_payment(call.from_user.id, product["name"], description, product["price"], secret_key.hexdigest())
    else:
        await call.message.edit_text(config.message["product_missing"])
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.wait)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_confirmation_no"])
    await SellInfo.description.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=SellInfo.wait)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=choice_buttons.getProductsKeyboard())
    await state.finish()
