from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp
from states.create_promoCode import CodeAdd
from states.edit_promoCode import CodeEdit
from utils.db_api.models import promoCodesModel
from utils import function


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
async def start_create_code(message: types.Message, state: FSMContext):
    await CodeAdd.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_name"], reply_markup=menu)


@dp.message_handler(state=CodeAdd.name, user_id=config.ADMINS)
async def create_code_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await CodeAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=CodeAdd.code, user_id=config.ADMINS)
async def create_code_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await CodeAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=CodeAdd.percent, user_id=config.ADMINS)
async def create_code_percent(message: types.Message, state: FSMContext):
    if message.text == "1" or message.text == "2":
        await state.update_data(percent=(message.text == "2"))
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))
    else:
        await message.answer(text="Вы указали неверное число, повторите попытку.")


@dp.message_handler(state=CodeAdd.discount, user_id=config.ADMINS)
async def create_code_discount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit() and (data.get("percent") and int(message.text) <= 95):
        await state.update_data(discount=message.text)
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))
    else:
        await message.answer(text="Вы указали не число, либо при скидки в процентах привысили 95%, повторите попытку.")


@dp.message_handler(state=CodeAdd.wait)
async def waiting(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=CodeAdd)
async def create_code_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = ""
    if "CodeAdd:discount" == state_active:
        promoCodesModel.create_promo_code(data.get("name"), data.get("code"), data.get("percent"), data.get("discount"))
        await CodeAdd.next()
        await state.finish()
        await call.message.edit_text("Сохранено")
        return
    elif "CodeAdd:percent" == state_active:
        await CodeAdd.discount.set()
        mes = config.adminMessage["code_add_discount"]
    elif "CodeAdd:code" == state_active:
        await CodeAdd.percent.set()
        mes = config.adminMessage["code_add_percent"]
    elif "CodeAdd:name" == state_active:
        await CodeAdd.code.set()
        mes = config.adminMessage["code_add_code"]
    await function.set_state_active(state)
    await call.message.edit_text(text=mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeAdd)
async def create_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    if "CodeAdd:discount" == state_active:
        await CodeAdd.discount.set()
    elif "CodeAdd:percent" == state_active:
        await CodeAdd.percent.set()
    elif "CodeAdd:code" == state_active:
        await CodeAdd.code.set()
    elif "CodeAdd:name" == state_active:
        await CodeAdd.name.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_repeat"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=CodeAdd)
async def create_code_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["code_add_cancel"])
    await state.finish()


### Изменение промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeEdit"])
async def start_edit_code(message: types.Message, state: FSMContext):
    mes = config.adminMessage["code_missing"]
    code = promoCodesModel.get_promo_code_id(function.checkID(message.text))
    if code["success"]:
        await state.update_data(codeEditID=code["id"])
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
    await CodeEdit.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_name"])


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["code"])
async def edit_code_code_start(message: types.Message, state: FSMContext):
    await CodeEdit.code.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_code"])


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["type"])
async def edit_code_type_start(message: types.Message, state: FSMContext):
    await CodeEdit.percent.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_percent"])


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["discount"])
async def edit_code_discount_start(message: types.Message, state: FSMContext):
    await CodeEdit.discount.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_discount"])


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["delete"])
async def edit_code_delete_start(message: types.Message, state: FSMContext):
    await CodeEdit.delete.set()
    await function.set_state_active(state)
    await message.answer("Удалить промокод", reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.zero, user_id=config.ADMINS, commands=["back"])
async def edit_code_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(config.adminMessage["code_edit_back"])


@dp.message_handler(state=CodeEdit.name, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.code, user_id=config.ADMINS)
async def edit_code_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.percent, user_id=config.ADMINS)
async def edit_code_percent(message: types.Message, state: FSMContext):
    if message.text == "1" or message.text == "2":
        await state.update_data(percent=message.text == "2")
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы указали неверное число, повторите попытку.")


@dp.message_handler(state=CodeEdit.discount, user_id=config.ADMINS)
async def edit_code_discount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = promoCodesModel.get_promo_code_id(data.get("codeEditID"))
    if code["success"] and message.text.isdigit() and (code["percent"] and int(message.text) <= 95):
        await state.update_data(discount=message.text)
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы указали не число, либо при скидки в процентах привысили 95%, повторите попытку.")


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=CodeEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    state_active = data.get("state_active")
    code = promoCodesModel.get_promo_code_id(data.get("codeEditID"))
    if not code["success"]:
        await state.finish()
        await call.message.edit_text(config.adminMessage["code_missing"])
        return

    if "CodeEdit:delete" == state_active:
        promoCodesModel.delete_promo_code(code["id"])
        await state.finish()
        await call.message.edit_text(text=config.adminMessage["code_del_yes"])
        return

    if "CodeEdit:name" == state_active:
        code["name"] = data.get("name") if "name" in keys else ""
    elif "CodeEdit:code" == state_active:
        code["code"] = data.get("code") if "code" in keys else ""
    elif "CodeEdit:percent" == state_active:
        code["percent"] = data.get("percent") if "percent" in keys else ""
    elif "CodeEdit:discount" == state_active:
        code["discount"] = data.get("discount") if "discount" in keys else ""
    promoCodesModel.update_promo_code(code["id"], code["name"], code["code"], code["percent"], code["discount"])
    await CodeEdit.zero.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_edit"].format(name=code["name"],
                                                                         code=code["code"],
                                                                         typeD="Скидка в процентах" if code[
                                                                             "percent"] else "Скидка определенной суммы",
                                                                         discount=str(code["discount"]) + (
                                                                             "%" if code["percent"] else " р.")))


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = config.adminMessage["code_add_repeat"]
    if "CodeEdit:delete" == state_active:
        mes = config.adminMessage["code_del_no"]
    await CodeEdit.zero.set()
    await function.set_state_active(state)
    await call.message.edit_text(mes)

