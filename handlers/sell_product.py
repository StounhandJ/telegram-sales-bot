from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback
from keyboards.inline import choice_buttons
from loader import dp
from data import config
from utils.db_api import models
from states.sell_info import SellInfo


@dp.callback_query_handler(buy_callback.filter())
async def product_info(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    async with state.proxy() as data:
        data["productID"] = callback_data["id"]
    product = models.get_product(callback_data["id"])
    if product["success"]:
        await call.message.edit_text(
            text=config.message["product_info"].format(item_name=product["name"], price=product["price"], description=product["description"]),
            reply_markup=choice_buttons.getSellProductsKeyboard())
    else:
        await call.message.edit_text(config.errorMessage["product_missing"])


@dp.callback_query_handler(setting_callback.filter(command="exit"))
async def show_product(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["productID"] = ""
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=choice_buttons.getProductsKeyboard())


@dp.callback_query_handler(setting_callback.filter(command="add"))
async def comment_order(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_order"])
    await SellInfo.description.set()


@dp.message_handler(state=SellInfo.description)
async def comment_confirmation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(config.message["comment_confirmation"].format(text=message.text), reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.description)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    models.create_order(call.from_user.id, data.get("productID"), data.get("description"))
    await call.message.edit_text(config.message["comment_confirmation_yes"])
    # тут заявка отправляеться админам
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.description)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_confirmation_no"])
