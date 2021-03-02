from aiogram import types
from aiogram.dispatcher import FSMContext
from re import *

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import setting_callback, confirmation_callback, type_work_callback
from loader import dp, bot
from states.user_sell_info import SellInfo
from utils.db_api.models import ordersProcessingModel, promoCodesModel, banListModel, userInformationModel
from utils.notify_admins import notify_admins_message
from utils import function


@dp.callback_query_handler(type_work_callback.filter(work="other_works"))
async def diploma_info(call: types.CallbackQuery):
    await call.message.edit_text(text="Другие работы",
                                 reply_markup=await buttons.getOtherWorks())
    await call.answer()


@dp.callback_query_handler(type_work_callback.filter(work="back"))
async def diploma_info(call: types.CallbackQuery):
    await call.message.edit_text(text=config.message["Product_Menu"], reply_markup=await buttons.getTypeWorkKeyboard())
    await call.answer()


@dp.callback_query_handler(type_work_callback.filter())
async def diploma_info(call: types.CallbackQuery, callback_data: dict):
    await call.message.edit_text(text=config.works[callback_data["work"]]["description"],
                                 reply_markup=await buttons.getSellWorkKeyboard(callback_data["work"]))
    await call.answer()


@dp.callback_query_handler(setting_callback.filter(command="exit"))
async def product_info_exit(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=await buttons.getTypeWorkKeyboard())
    await call.answer()


@dp.callback_query_handler(setting_callback.filter(command="continue"))
async def start_buy_product(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    if banListModel.is_ban_user(call.from_user.id):
        await call.message.edit_text("Вы забанены")
        return

    await state.update_data(type_work=callback_data["type"])
    await SellInfo.description.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.works[callback_data["type"]]["template"],
                                 reply_markup=await buttons.getCustomKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=SellInfo.description)
async def adding_comment(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(description=message.text)
    await SellInfo.wait.set()
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=SellInfo.email)
async def adding_comment(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    if pattern.match(message.text):
        await state.update_data(email=message.text)
        await SellInfo.wait.set()
        await message.answer(config.message["email_confirmation"].format(text=message.text),
                             reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
    else:
        await message.answer(config.message["comment_email_no_validation"].format(text=message.text),
                             reply_markup=await buttons.getCustomKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=SellInfo.wait)
async def waiting(message: types.Message):
    pass


@dp.message_handler(state=SellInfo.document, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document)
    await SellInfo.wait.set()
    await message.answer(config.message["document_confirmation"].format(
        text="{name} {size}кб\n".format(name=message.document.file_name, size=message.document.file_size)),
        reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=SellInfo.document, content_types=types.ContentType.PHOTO)
async def message_add_doc(message: types.Message):
    await message.answer(text=config.errorMessage["not_add_photo"])


@dp.message_handler(state=SellInfo.promoCode)
async def adding_promoCode(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    code = promoCodesModel.get_promo_code(message.text)
    if code and code.limitation_use and code.count <= 0:
        await message.answer("Данный промокод закончился")
    elif code:
        await state.update_data(percent=code.percent,
                                discount=code.discount,
                                promoCode=code.code)
        await SellInfo.wait.set()
        await message.answer(config.message["promoCode_confirmation"].format(name=code.name,
                                                                             discount=str(code.discount) + (
                                                                                 "%" if code.percent else " р.")),
                             reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
    else:
        await message.answer(text=config.message["code_missing"]+"\n"+config.message["comment_confirmation_no"], reply_markup=await buttons.getCustomKeyboard(cancel="Отменить заказ"))


@dp.callback_query_handler(confirmation_callback.filter(bool="noElement"), state=SellInfo)
async def adding_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = ""
    state_active = data.get("state_active")
    keyboard = None
    if "SellInfo:promoCode" == state_active:
        await SellInfo.separatePayment.set()
        await function.set_state_active(state)
        mes = config.message["separatePayment"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:document" == state_active:
        await SellInfo.promoCodeCheck.set()
        await function.set_state_active(state)
        mes = config.message["comment_promoCodeCheck"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    await call.message.edit_text(text=mes, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo)
async def adding_comment_or_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = ""
    state_active = data.get("state_active")
    keyboard = None
    if "SellInfo:separatePayment" == state_active:
        await state.update_data(separatePayment=False)
        await create_order(call, state)
        return
    elif "SellInfo:promoCode" == state_active:
        await SellInfo.separatePayment.set()
        mes = config.message["separatePayment"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:promoCodeCheck" == state_active:
        await SellInfo.promoCode.set()
        mes = config.message["comment_promoCode"]
        keyboard = await buttons.getCustomKeyboard(noElement="Нет промокода")
    elif "SellInfo:document" == state_active:
        await SellInfo.promoCodeCheck.set()
        mes = config.message["comment_promoCodeCheck"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:documentCheck" == state_active:
        await SellInfo.document.set()
        mes = config.message["comment_document"]
        keyboard = await buttons.getCustomKeyboard(noElement="Нет файла")
    elif "SellInfo:email" == state_active:
        await SellInfo.documentCheck.set()
        description = data["type_work"] + "\n\n" + data.get("description")
        await state.update_data(description=description)
        mes = config.message["comment_documentCheck"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:description" == state_active:
        await SellInfo.email.set()
        mes = config.message["comment_email"]
        keyboard = await buttons.getCustomKeyboard(cancel="Отменить заказ")
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo)
async def adding_comment_or_promoCode_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = config.message["comment_confirmation_no"]
    keyboard = await buttons.getCustomKeyboard(cancel="Отменить заказ")
    if "SellInfo:promoCode" == state_active:
        await SellInfo.promoCode.set()
    elif "SellInfo:document" == state_active:
        await SellInfo.document.set()
    elif "SellInfo:description" == state_active:
        await SellInfo.description.set()
    elif "SellInfo:email" == state_active:
        await SellInfo.email.set()
    elif "SellInfo:documentCheck" == state_active:
        await SellInfo.promoCodeCheck.set()
        mes = config.message["comment_promoCodeCheck"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:promoCodeCheck" == state_active:
        await SellInfo.separatePayment.set()
        mes = config.message["separatePayment"]
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "SellInfo:separatePayment" == state_active:
        await state.update_data(separatePayment=True)
        await create_order(call, state)
        return
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=SellInfo)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=await buttons.getTypeWorkKeyboard())
    await call.answer()


async def create_order(call, state):
    data = await state.get_data()
    document = [data.get("document").file_id] if "document" in data.keys() else []
    email = data.get("email") if "email" in data.keys() else ""
    description = data.get("description") if "description" in data.keys() else ""
    percent = data.get("percent") if "percent" in data.keys() else False
    discount = data.get("discount") if "discount" in data.keys() else 0
    promoCode = data.get("promoCode") if "promoCode" in data.keys() else ""
    separatePayment = data.get("separatePayment") if "separatePayment" in data.keys() else True
    ordersProcessingModel.create_order_provisional(call.from_user.id, description, document,
                                                   separatePayment, percent,
                                                   discount)
    promoCodesModel.promo_code_used(promoCode)
    userInformationModel.update_email(call.from_user.id, email)
    await notify_admins_message(config.adminMessage["admin_mes_order_provisional"])
    await state.finish()
    mes = config.message["order_send"]
    await call.message.edit_text(text=mes)
