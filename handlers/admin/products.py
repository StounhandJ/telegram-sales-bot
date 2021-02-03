from aiogram import types
from aiogram.dispatcher import FSMContext
from data import config
from states.product_add import ProductAdd
from states.product_edit import ProductEdit
from states.admin_mes_order import AdminMesOrder
from keyboards.inline import choice_buttons
from keyboards.inline.callback_datas import confirmation_callback
from keyboards.default import menu
from loader import dp
from utils.db_api import models


### Информация о продукте ###

@dp.message_handler(user_id=config.ADMINS, commands=["productList"])
async def show_productList(message: types.Message):
    mes = config.adminMessage["products_missing"]
    products = models.get_ALLProducts()
    if products["success"]:
        mes = config.adminMessage["products_main"]
        num = 1
        for product in products["data"]:
            mes += config.adminMessage["product_info"].format(num=num, orderID=product["id"], name=product["name"],
                                                              price=product["price"],
                                                              description=product["description"])
            num += 1
    await message.answer(mes, reply_markup=menu)


### Создзание продукта ###

@dp.message_handler(user_id=config.ADMINS, commands=["addProduct"])
async def start_create_product(message: types.Message):
    await ProductAdd.name.set()
    await message.answer(config.adminMessage["product_add_name"], reply_markup=menu)


@dp.message_handler(state=ProductAdd.name, user_id=config.ADMINS)
async def create_product_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.message_handler(state=ProductAdd.description, user_id=config.ADMINS)
async def create_product_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.message_handler(state=ProductAdd.price, user_id=config.ADMINS)
async def create_product_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard(cancel="Отменить заказ"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=ProductAdd)
async def create_product_yes(call: types.CallbackQuery, state: FSMContext):
    await ProductAdd.next()
    data = await state.get_data()
    keys = data.keys()
    if "price" in keys:
        models.create_product(data.get("name"), data.get("description"), data.get("price"))
        mes = "Сохранено"
        await ProductAdd.next()
        await state.finish()
    elif "description" in keys:
        mes = config.adminMessage["product_add_price"]
    elif "name" in keys:
        mes = config.adminMessage["product_add_description"]
    else:
        mes = "Ошибка!!!!"
    await call.message.edit_text(mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=ProductAdd)
async def create_product_no(call: types.CallbackQuery):
    await call.message.edit_text(config.adminMessage["product_add_repeat"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=ProductAdd)
async def create_product_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.message["product_add_cancel"])
    await state.finish()


### Изменение продукта ###

@dp.message_handler(user_id=config.ADMINS, commands=["productEdit"])
async def start_edit_product(message: types.Message, state: FSMContext):
    mes = config.adminMessage["product_missing"]
    product = models.get_product(checkID(message.text))
    if product["success"]:
        async with state.proxy() as data:
            data["productEditID"] = product["id"]
        mes = config.adminMessage["product_edit"].format(name=product["name"],
                                                         price=product["price"],
                                                         description=product["description"])
        await ProductEdit.zero.set()
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=ProductEdit.zero, user_id=config.ADMINS, commands=["name"])
async def edit_product_name_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["product_add_name"])
    await ProductEdit.name.set()


@dp.message_handler(state=ProductEdit.zero, user_id=config.ADMINS, commands=["description"])
async def edit_product_description_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["product_add_description"])
    await ProductEdit.description.set()


@dp.message_handler(state=ProductEdit.zero, user_id=config.ADMINS, commands=["price"])
async def edit_product_price_start(message: types.Message, state: FSMContext):
    await message.answer(config.adminMessage["product_add_price"])
    await ProductEdit.price.set()


@dp.message_handler(state=ProductEdit.zero, user_id=config.ADMINS, commands=["back"])
async def edit_product_back(message: types.Message, state: FSMContext):
    await AdminMesOrder.last()
    await AdminMesOrder.next()
    await state.finish()
    await message.answer(config.adminMessage["product_edit_back"])


@dp.message_handler(state=ProductEdit.name, user_id=config.ADMINS)
async def edit_product_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.message_handler(state=ProductEdit.description, user_id=config.ADMINS)
async def edit_product_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.message_handler(state=ProductEdit.price, user_id=config.ADMINS)
async def edit_product_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text
    await message.answer(message.text + "\n" + config.adminMessage["product_add_confirmation"],
                         reply_markup=choice_buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=ProductEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keys = data.keys()
    product = models.get_product(data.get("productEditID"))
    if not product["success"]:
        await AdminMesOrder.last()
        await AdminMesOrder.next()
        await state.finish()
        await call.message.edit_text(config.adminMessage["product_missing"])
        return

    if "price" in keys:
        product["price"] = data.get("price")
    elif "description" in keys:
        product["description"] = data.get("description")
    elif "name" in keys:
        product["name"] = data.get("name")
    models.update_product(product["id"], product["name"], product["description"], product["price"], )
    await call.message.edit_text(
        "<b>Обновленно</b>\n" + config.adminMessage["product_edit"].format(name=product["name"],
                                                                           price=product["price"],
                                                                           description=product["description"]))
    await ProductEdit.zero.set()


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=ProductEdit)
async def edit_product_no(call: types.CallbackQuery):
    await call.message.edit_text(config.adminMessage["product_add_repeat"])


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1
