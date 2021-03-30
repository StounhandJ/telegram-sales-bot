import math

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback, numbering_callback
from loader import dp
from states.admin_create_promoCode import CodeAdd
from states.admin_edit_promoCode import CodeEdit
from utils.db_api.models import promoCodesModel
from utils import function


### Информация о промокодах ###

@dp.message_handler(Text(equals=["Промокоды", "/codes"]), user_id=config.ADMINS)
async def show_codeList(message: types.Message):
    mes, keyboard = await menu_main(0)
    await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(numbering_callback.filter(what_action="PromoCodeNumbering"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, callback_data: dict):
    mes, keyboard = await menu_main(int(callback_data["number"]))
    try:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    except:
        await call.answer(cache_time=1)


### Создзание промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeAdd"])
async def start_create_code(message: types.Message, state: FSMContext):
    await CodeAdd.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["code_add_name"])


@dp.message_handler(state=CodeAdd.name, user_id=config.ADMINS)
async def create_code_name(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(name=message.text)
    await CodeAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=CodeAdd.code, user_id=config.ADMINS)
async def create_code_code(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    promoCodes = promoCodesModel.get_ALLPromoCode()
    if not (promoCodes and message.text in [promo.code for promo in promoCodes]):
        await state.update_data(code=message.text)
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить создание"))
    else:
        await message.answer("Такой промокод уже существует",
                             reply_markup=await buttons.getCustomKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=CodeAdd.count, user_id=config.ADMINS)
async def create_code_percent(message: types.Message, state: FSMContext):
    if message.text.isdigit() and 0 < int(message.text) < 9999999:
        await state.update_data(count=int(message.text))
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить создание"))
    else:
        await message.answer("Вы указали неправильное число")


@dp.callback_query_handler(confirmation_callback.filter(), state=CodeAdd.percent, user_id=config.ADMINS)
async def create_code_percent(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    typeDiscount = callback_data.get("bool")
    if typeDiscount == "percent" or typeDiscount == "amount":
        await state.update_data(IsPercent=(typeDiscount == "percent"))
        await CodeAdd.discount.set()
        await function.set_state_active(state)
        await call.message.edit_text(config.adminMessage["code_add_discount"])
    else:
        await call.answer(text="Вы потерялись...")


@dp.message_handler(state=CodeAdd.discount, user_id=config.ADMINS)
async def create_code_discount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit() and (not data.get("percent") or (data.get("percent") and int(message.text) <= 95)):
        await state.update_data(discount=message.text)
        await CodeAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить создание"))
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
    keyboard = None
    if "CodeAdd:discount" == state_active:
        count = data.get("count") if "limitationUse" in data.keys() else 99999999
        promoCodesModel.create_promo_code(data.get("name"), data.get("code"), data.get("IsPercent"), data.get("discount"), count)
        await CodeAdd.next()
        await state.finish()
        await call.message.edit_text("Сохранено")
        return
    elif "CodeAdd:count" == state_active:
        await CodeAdd.percent.set()
        mes = config.adminMessage["code_add_percent"]
        keyboard = await buttons.getCustomKeyboard(percent="Проценты", amount="Сумма")
    elif "CodeAdd:limitationUse" == state_active:
        await state.update_data(limitationUse=True)
        await CodeAdd.count.set()
        mes = "Укажите количество промокодов: "
    elif "CodeAdd:code" == state_active:
        await CodeAdd.limitationUse.set()
        mes = "Ограниченное количество использований?"
        keyboard = await buttons.getConfirmationKeyboard(cancel="Отменить создание")
    elif "CodeAdd:name" == state_active:
        await CodeAdd.code.set()
        mes = config.adminMessage["code_add_code"]
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeAdd)
async def create_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = config.adminMessage["code_add_repeat"]
    keyboard = None
    if "CodeAdd:discount" == state_active:
        await CodeAdd.discount.set()
    elif "CodeAdd:count" == state_active:
        await CodeAdd.count.set()
    elif "CodeAdd:limitationUse" == state_active:
        await CodeAdd.percent.set()
        mes = config.adminMessage["code_add_percent"]
        keyboard = await buttons.getCustomKeyboard(percent="Проценты", amount="Сумма")
    elif "CodeAdd:code" == state_active:
        await CodeAdd.code.set()
    elif "CodeAdd:name" == state_active:
        await CodeAdd.name.set()
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=CodeAdd)
async def create_code_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["code_add_cancel"])
    await state.finish()


### Изменение промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["codeEdit"])
async def start_edit_code(message: types.Message):
    mes, keyboard = await menu_edit_promoCode(function.checkID(message.text))
    await message.answer(mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="promoCode_name"), user_id=config.ADMINS)
async def edit_code_name_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await CodeEdit.name.set()
    await state.update_data(codeEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_name"],
                                 reply_markup=await buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="promoCode_code"), user_id=config.ADMINS)
async def edit_code_code_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await CodeEdit.code.set()
    await state.update_data(codeEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_code"],
                                 reply_markup=await buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="promoCode_discount"), user_id=config.ADMINS)
async def edit_code_discount_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await CodeEdit.discount.set()
    await state.update_data(codeEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_discount"],
                                 reply_markup=await buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="promoCode_count"), user_id=config.ADMINS)
async def edit_code_discount_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await CodeEdit.count.set()
    await state.update_data(codeEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text("Укажите новое количество промокодов:",
                                 reply_markup=await buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="promoCode_delete"), user_id=config.ADMINS)
async def edit_code_delete_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await CodeEdit.delete.set()
    await state.update_data(codeEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text("Удалить промокод", reply_markup=await buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.name, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(name=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=await buttons.getConfirmationKeyboard())


@dp.message_handler(state=CodeEdit.code, user_id=config.ADMINS)
async def edit_code_code(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    promoCodes = promoCodesModel.get_ALLPromoCode()
    if not (promoCodes and message.text in [promo.code for promo in promoCodes]):
        await state.update_data(code=message.text)
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer("Такой промокод уже существует")


@dp.message_handler(state=CodeEdit.percent, user_id=config.ADMINS)
async def edit_code_percent(message: types.Message, state: FSMContext):
    if message.text == "1" or message.text == "2":
        await state.update_data(IsPercent=message.text == "2")
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы указали неверное число, повторите попытку.")


@dp.message_handler(state=CodeEdit.discount, user_id=config.ADMINS)
async def edit_code_discount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code = promoCodesModel.get_promo_code_id(data.get("codeEditID"))
    if code and message.text.isdigit() and (
            not data.get("IsPercent") or (data.get("IsPercent") and int(message.text) <= 95)):
        await state.update_data(discount=message.text)
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer(text="Вы указали не число, либо при скидки в процентах привысили 95%, повторите попытку.")


@dp.message_handler(state=CodeEdit.count, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    if message.text.isdigit() and 0 < int(message.text) < 9999999:
        await state.update_data(count=message.text)
        await message.answer(text=message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=await buttons.getConfirmationKeyboard())
    else:
        await message.answer("Вы указали неправильное число")


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=CodeEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    code = promoCodesModel.get_promo_code_id(data.get("codeEditID"))
    if not code:
        await state.finish()
        await call.message.edit_text(config.adminMessage["code_missing"])
        return
    if "CodeEdit:delete" == state_active:
        promoCodesModel.delete_promo_code(code.id)
        await state.finish()
        await call.message.edit_text(text=config.adminMessage["code_del_yes"])
        return
    if "CodeEdit:name" == state_active:
        code.name = data.get("name")
    elif "CodeEdit:code" == state_active:
        code.code = data.get("code")
    elif "CodeEdit:discount" == state_active:
        code.discount = data.get("discount")
    elif "CodeEdit:count" == state_active:
        code.limitation_use = data.get("count")
    code.save()
    mes, keyboard = await menu_edit_promoCode(data.get("codeEditID"))
    await state.finish()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=CodeEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes, keyboard = await menu_edit_promoCode(data.get("codeEditID"))
    await state.finish()
    await call.message.edit_text(mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=CodeEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes, keyboard = await menu_edit_promoCode(data.get("codeEditID"))
    await state.finish()
    await call.message.edit_text(mes, reply_markup=keyboard)


async def menu_edit_promoCode(codeEditID):
    code = promoCodesModel.get_promo_code_id(codeEditID)
    if code:
        keyboard = await buttons.getActionKeyboard(code.id, promoCode_name="Имя", promoCode_code="Промокод",
                                                   promoCode_discount="Скидка", promoCode_count="Количество",
                                                   promoCode_delete="Удалить")
        return [config.adminMessage["code_edit"].format(name=code.name, code=code.code,
                                                        count=code.limitation_use,
                                                        discount=code.info),
                keyboard]
    else:
        return [config.adminMessage["code_missing"], None]


async def menu_main(page):
    mes = config.adminMessage["codes_missing"]
    keyboard = None
    codes = promoCodesModel.get_promoCode(page, config.max_size_promoCode)
    promoCode_count = promoCodesModel.get_ALLPromoCode_count()
    if codes:
        text = ""
        num = 1
        for code in codes:
            text += config.adminMessage["code_info"].format(num=num + (page * config.max_size_promoCode), id=code.id,
                                                            name=code.name,
                                                            code=code.code,
                                                            count=code.limitation_use,
                                                            discount=code.info)
            num += 1
        mes = config.adminMessage["code_main"].format(text=text)
        keyboard = await buttons.getNumbering(math.ceil(promoCode_count / config.max_size_promoCode),
                                              "PromoCodeNumbering")
    return mes, keyboard
