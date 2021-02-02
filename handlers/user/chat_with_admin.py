from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text
from keyboards.inline.callback_datas import confirmation_callback
from keyboards.inline import choice_buttons
from loader import dp
from data import config
from states.user_mes import UserMes
from utils.db_api import models


@dp.message_handler(Text(equals=["Написать администрации"]))
async def show_menu(message: types.Message):
    await UserMes.message.set()
    await message.answer("Напишите свое сообщение:")


@dp.message_handler(commands=["mesa", "ames", "Ames", "mesA"])
async def show_menu(message: types.Message):
    await UserMes.message.set()
    await message.answer("Напишите свое сообщение:")


@dp.message_handler(state=UserMes.message)
async def comment_confirmation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["message"] = message.text
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=choice_buttons.getConfirmationKeyboard(cancel="Отменить"))
    await UserMes.wait.set()


@dp.message_handler(state=UserMes.wait)
async def comment_confirmation(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=UserMes.wait)
async def comment_confirmation_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    orders = models.get_ALLOrders()
    isOrder = orders["success"] and call.from_user.id in [order["userID"] for order in orders["data"]]
    models.create_messages(call.from_user.id,
                           data.get("message") if "message" in data.keys() else "", isOrder)
    for admin in config.ADMINS:
        await dp.bot.send_message(admin, "Новое сообщение от "+ ("<b>пользователя с заказом</b>" if isOrder else "<b>обычного пользователя</b>"))
    await call.message.edit_text(config.message["message_sent"])
    await state.finish()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=UserMes.wait)
async def comment_confirmation_no(call: types.CallbackQuery):
    await call.message.edit_text(config.message["message_no"])
    await UserMes.message.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=UserMes.wait)
async def comment_confirmation_no(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["message_cancel"])
    await state.finish()
