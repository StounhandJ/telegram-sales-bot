from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.callback_datas import buy_callback, setting_callback, confirmation_callback
from keyboards.inline.choice_buttons import sell_products_keyboard, products, confirmation
from loader import dp
from data import config
from states.sell_info import SellInfo


@dp.callback_query_handler(buy_callback.filter())
async def product_info(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=2)
    item_name = callback_data["item_name"]
    price = callback_data["price"]
    async with state.proxy() as data:
        data["product"] = item_name
    await call.message.edit_text(text=config.message["product_info"].format(item_name=item_name, price=price),
                                 reply_markup=sell_products_keyboard)


@dp.callback_query_handler(setting_callback.filter(command="exit"))
async def show_product(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["product"] = ""
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=products)


@dp.callback_query_handler(setting_callback.filter(command="add"))
async def comment_order(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_order"])
    await SellInfo.description.set()


@dp.message_handler(state=SellInfo.description)
async def comment_confirmation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(config.message["comment_confirmation"].format(text=message.text), reply_markup=confirmation)


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.description)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_confirmation_yes"])
    # тут заявка отправляеться админам
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.description)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["comment_confirmation_no"])
