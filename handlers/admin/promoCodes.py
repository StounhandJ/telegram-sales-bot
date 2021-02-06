from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp
from states.admin_mes_order import AdminMesOrder
from states.create_promoCode import CodeAdd
from states.edit_code import CodeEdit
from utils.db_api.models import promoCodesModel


### Информация о промокодах ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeList"])
async def show_codeList(message: types.Message):
    mes = config.adminMessage["codes_missing"]
    codes = promoCodesModel.get_ALLPromoCode()
    if codes["success"]:
        text = ""
        num = 1
        for code in codes["data"]:
            discount = str(code["discount"]) + ("%" if code["percent"] else " р.")
            text += config.adminMessage["code_info"].format(num=num, id=code["id"], name=code["name"],
                                                            discount=discount)
            num += 1
        mes = config.adminMessage["code_main"].format(text=text)
    await message.answer(mes, reply_markup=menu)


### Создзание промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeAdd"])
async def start_create_code(message: types.Message):
    await CodeAdd.name.set()
    await message.answer(config.adminMessage["code_add_name"], reply_markup=menu)


@dp.message_handler(state=CodeAdd.name, user_id=config.ADMINS)
async def create_code_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=CodeAdd.code, user_id=config.ADMINS)
async def create_code_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["code"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.message_handler(state=CodeAdd.percent, user_id=config.ADMINS)
async def create_code_percent(message: types.Message, state: FSMContext):
    if message.text == "1" or message.text == "2":
        async with state.proxy() as data:
            data["percent"] = message.text == "2"
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))
    else:
        await message.answer(text="Вы указали неверное число, повторите попытку.")


@dp.message_handler(state=CodeAdd.discount, user_id=config.ADMINS)
async def create_code_discount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["discount"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=CodeAdd)
async def create_code_yes(call: types.CallbackQuery, state: FSMContext):
    await CodeAdd.next()
    data = await state.get_data()
    keys = data.keys()
    if "discount" in keys:
        promoCodesModel.create_promo_code(data.get("name"), data.get("code"), data.get("percent"), data.get("discount"))
        mes = "Сохранено"
        await CodeAdd.next()
        await state.finish()
    elif "percent" in keys:
        mes = config.adminMessage["code_add_discount"]
    elif "code" in keys:
        mes = config.adminMessage["code_add_percent"]
    elif "name" in keys:
        mes = config.adminMessage["code_add_code"]
    else:
        mes = "Ошибка!!!!"
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeAdd)
async def create_code_no(call: types.CallbackQuery):
    await call.message.edit_text(config.adminMessage["code_add_repeat"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=CodeAdd)
async def create_code_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["code_add_cancel"])
    await state.finish()


### Изменение промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeEdit"])
async def start_edit_code(message: types.Message, state: FSMContext):
    mes = config.adminMessage["code_missing"]
    code = promoCodesModel.get_promo_code_id(checkID(message.text))
    if code["success"]:
        async with state.proxy() as data:
            data["codeEditID"] = code["id"]
        mes = config.adminMessage["code_edit"].format(name=code["name"],
                                                      code=code["code"],
                                                      typeD="Скидка в процентах" if code[
                                                          "percent"] else "Скидка определенной суммы",
                                                      discount=str(code["discount"]) + (
                                                          "%" if code["percent"] else " р."))
        await CodeEdit.zero.set()
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["name"])
async def edit_code_name_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["code_add_name"])
    await CodeEdit.name.set()


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["code"])
async def edit_code_code_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["code_add_code"])
    await CodeEdit.code.set()


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["type"])
async def edit_code_type_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["code_add_percent"])
    await CodeEdit.percent.set()


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["discount"])
async def edit_code_discount_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["code_add_discount"])
    await CodeEdit.discount.set()


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["delete"])
async def edit_code_delete_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["delete"] = True
    await message.answer("Удалить промокод", reply_markup=buttons.getConfirmationKeyboard())
    await CodeEdit.delete.set()


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["back"])
async def edit_code_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(config.adminMessage["code_edit_back"])


@dp.message_handler(state=CodeEdit.name, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.code, user_id=config.ADMINS)
async def edit_code_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["code"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.percent, user_id=config.ADMINS)
async def edit_code_percent(message: types.Message, state: FSMContext):
    if message.text == "1" or message.text == "2":
        async with state.proxy() as data:
            data["percent"] = message.text == "2"
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы указали неверное число, повторите попытку.")


@dp.message_handler(state=CodeEdit.discount, user_id=config.ADMINS)
async def edit_code_discount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["discount"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=CodeEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    code = promoCodesModel.get_promo_code_id(data.get("codeEditID"))
    if not code["success"]:
        await state.finish()
        await call.message.edit_text(config.adminMessage["code_missing"])
        return

    if "delete" in keys:
        promoCodesModel.delete_promo_code(code["id"])
        await state.finish()
        return
    if "name" in keys:
        code["name"] = data.get("name")
    elif "code" in keys:
        code["code"] = data.get("code")
    elif "percent" in keys:
        code["percent"] = data.get("percent")
    elif "discount" in keys:
        code["discount"] = data.get("discount")
    promoCodesModel.update_promo_code(code["id"], code["name"], code["code"], code["percent"], code["discount"])
    await call.message.edit_text(config.adminMessage["code_edit"].format(name=code["name"],
                                                                         code=code["code"],
                                                                         typeD="Скидка в процентах" if code[
                                                                             "percent"] else "Скидка определенной суммы",
                                                                         discount=str(code["discount"]) + (
                                                                             "%" if code["percent"] else " р.")))
    await CodeEdit.zero.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    mes = config.adminMessage["code_add_repeat"]
    if "delete" in keys:
        mes = config.adminMessage["code_del_no"]
        await CodeEdit.zero.set()
    await call.message.edit_text(mes)


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
