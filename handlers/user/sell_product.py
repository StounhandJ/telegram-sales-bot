from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import setting_callback, confirmation_callback, type_work_callback
from loader import dp
from states.sell_info import SellInfo
from utils.db_api.models import ordersProcessingModel, promoCodesModel
from utils.notify_admins import notify_admins_message


@dp.callback_query_handler(type_work_callback.filter(work="Coursework"))
async def coursework_info(call: types.CallbackQuery, callback_data: dict):
    await call.answer(cache_time=2)
    await call.message.edit_text(text="Информация о курсовой\n Цена от 3000 р.", reply_markup=buttons.getSellWorkKeyboard(callback_data["work"]))


@dp.callback_query_handler(type_work_callback.filter(work="Diploma"))
async def diploma_info(call: types.CallbackQuery, callback_data: dict):
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


@dp.message_handler(state=SellInfo.document, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["document"] = message.document
    await SellInfo.wait.set()
    await message.answer(config.message["document_confirmation"].format(text="{name} {size}кб\n".format(name=message.document.file_name, size=message.document.file_size)),
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=SellInfo.promoCode)
async def adding_promoCode(message: types.Message, state: FSMContext):
    code = promoCodesModel.get_promo_code(message.text)
    if code["success"]:
        async with state.proxy() as data:
            data["percent"] = code["percent"]
            data["discount"] = code["discount"]
        await message.answer(config.message["promoCode_confirmation"].format(name=code["name"], discount=str(code["discount"]) + ("%" if code["percent"] else " р.")),
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
        await SellInfo.wait.set()
    else:
        await message.answer(config.message["code_missing"])


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.documentCheck)
async def adding_promoCodeCheck_yes(call: types.CallbackQuery, state: FSMContext):
    await SellInfo.document.set()
    await call.message.edit_text(text=config.message["comment_document"],
                                 reply_markup=buttons.getCustomKeyboard(noDocument="Нет файла"))


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.documentCheck)
async def adding_promoCodeCheck_no(call: types.CallbackQuery, state: FSMContext):
    await SellInfo.promoCodeCheck.set()
    await call.message.edit_text(text=config.message["comment_promoCodeCheck"], reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.callback_query_handler(confirmation_callback.filter(bool="noDocument"), state=SellInfo.document)
async def adding_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    await SellInfo.promoCodeCheck.set()
    await call.message.edit_text(text=config.message["comment_promoCodeCheck"],
                                 reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.promoCodeCheck)
async def adding_promoCodeCheck_yes(call: types.CallbackQuery, state: FSMContext):
    await SellInfo.promoCode.set()
    await call.message.edit_text(text=config.message["comment_promoCode"],
                                 reply_markup=buttons.getCustomKeyboard(noPromo="Нет промокода"))


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.promoCodeCheck)
async def adding_promoCodeCheck_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    document = [data.get("document").file_id] if "document" in data.keys() else []
    ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), document, False, 0)
    await notify_admins_message(config.adminMessage["admin_mes_order_provisional"])
    await state.finish()
    await call.message.edit_text(text="Ваша заявка принята")


@dp.callback_query_handler(confirmation_callback.filter(bool="noPromo"), state=SellInfo.promoCode)
async def adding_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    document = [data.get("document").file_id] if "document" in data.keys() else []
    ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), document, False, 0)
    await state.finish()
    await call.message.edit_text(text="Ваша заявка принята")


@dp.message_handler(state=SellInfo.wait)
async def waiting(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=SellInfo.wait)
async def adding_comment_or_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    data = await state.get_data()
    keys = data.keys()
    mes = "Ошибка!!!"
    keyboard = None
    if "percent" in keys:
        document = [data.get("document").file_id] if "document" in data.keys() else []
        ordersProcessingModel.create_order_provisional(call.from_user.id, data.get("description"), document, data.get("percent"), data.get("discount"))
        await notify_admins_message(config.adminMessage["admin_mes_order_provisional"])
        mes = "Ваша заявка принята"
        await state.finish()
    elif "document" in keys:
        await SellInfo.promoCodeCheck.set()
        mes = config.message["comment_promoCodeCheck"]
        keyboard = buttons.getConfirmationKeyboard(cancel="Отменить заказ")
    elif "description" in keys:
        async with state.proxy() as data:
            data["description"] = ("Курсовая" if data["type_work"]=="Coursework" else "Дипломная")+"\n\n"+data["description"]
        mes = config.message["comment_documentCheck"]
        keyboard = buttons.getConfirmationKeyboard(cancel="Отменить заказ")
        await SellInfo.documentCheck.set()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=SellInfo.wait)
async def adding_comment_or_promoCode_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    if "percent" in keys:
        await SellInfo.promoCode.set()
    elif "document" in keys:
        await SellInfo.document.set()
    elif "description" in keys:
        await SellInfo.description.set()
    await call.message.edit_text(config.message["comment_confirmation_no"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=SellInfo)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["Product_Menu"], reply_markup=buttons.getTypeWorkKeyboard())
    await state.finish()
