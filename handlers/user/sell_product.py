import time

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import setting_callback, confirmation_callback, type_work_callback
from loader import dp, bot
from states.sell_info import SellInfo
from utils.db_api.models import paymentModel, orderModel, ordersProcessingModel, promoCodesModel


@dp.callback_query_handler(type_work_callback.filter(work="Coursework"))
async def product_info(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=2)
    await call.message.edit_text(text="Информация о курсовой\n Цена от 3000 р.", reply_markup=buttons.getSellWorkKeyboard(callback_data["work"]))


@dp.callback_query_handler(type_work_callback.filter(work="Diploma"))
async def product_info(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=2)
    await call.message.edit_text(text="Информация о дипломной работе\n Цена от 2000 р.", reply_markup=buttons.getSellWorkKeyboard(callback_data["work"]))


@dp.callback_query_handler(setting_callback.filter(command="exit"))
async def product_info_exit(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=buttons.getTypeWorkKeyboard())


@dp.callback_query_handler(setting_callback.filter(command="continue"))
async def start_buy_product(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    mes = "Ошибка"
    if callback_data["type"] == "Coursework":
        mes = config.message["Coursework"]
    elif callback_data["type"] == "Diploma":
        mes = config.message["Diploma"]
    async with state.proxy() as data:
        data["type_work"] = callback_data["type"]
    await SellInfo.description.set()
    await call.message.edit_text(mes)


@dp.message_handler(state=SellInfo.description)
async def adding_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
    await SellInfo.wait.set()


@dp.message_handler(state=SellInfo.promoCode)
async def adding_comment(message: types.Message, state: FSMContext):
    code = promoCodesModel.get_promo_code(message.text)
    if code["success"]:
        async with state.proxy() as data:
            data["percent"] = code["percent"]
            data["discount"] = code["discount"]
        codeInfo = config.message["code_info"].format(name=code["name"], discount=str(code["discount"]) + ("%" if code["percent"] else " р."))
        await message.answer(config.message["promoCode_confirmation"].format(text=codeInfo),
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
        await SellInfo.wait.set()
    else:
        await message.answer(config.message["code_missing"])


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.promoCodeCheck)
async def adding_comment_yes(call: types.CallbackQuery, state: FSMContext):
    await SellInfo.promoCode.set()
    await call.message.edit_text(text=config.message["comment_promoCode"],
                                 reply_markup=buttons.getCustomKeyboard(noPromo="Нет промокода"))


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.promoCodeCheck)
async def adding_comment_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), False, 0)
    await state.finish()
    await call.message.edit_text(text="Ваша заявка принята")


@dp.callback_query_handler(confirmation_callback.filter(bool="noPromo"), state=SellInfo.promoCode)
async def adding_comment_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), False, 0)
    await state.finish()
    await call.message.edit_text(text="Ваша заявка принята")


@dp.message_handler(state=SellInfo.wait)
async def waiting(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.wait)
async def adding_comment_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    keys = data.keys()
    mes = "Ошибка!!!"
    keyboard = None
    if "percent" in keys:
        ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), data.get("percent"), data.get("discount"))
        mes = "Ваша заявка принята"
        await state.finish()
    elif "description" in keys:
        async with state.proxy() as data:
            data["description"] = data["type_work"]+"\n\n"+data["description"]
        mes = config.message["comment_promoCodeCheck"]
        keyboard = buttons.getConfirmationKeyboard(cancel="Отменить заказ")
        await SellInfo.promoCodeCheck.set()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.wait)
async def adding_comment_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if "promoCodeCheck" in data.keys():
        async with state.proxy() as data:
            data["promoCode"] = ""
    await call.message.edit_text(config.message["comment_confirmation_no"])
    await SellInfo.description.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=SellInfo.promoCodeCheck)
async def adding_comment_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=buttons.getTypeWorkKeyboard())
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=SellInfo.wait)
async def adding_comment_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=buttons.getTypeWorkKeyboard())
    await state.finish()
