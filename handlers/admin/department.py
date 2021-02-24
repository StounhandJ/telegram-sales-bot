from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback
from loader import dp, bot
from states.admin_create_department import DepartmentAdd
from states.admin_edit_department import DepartmentEdit
from utils.db_api.models import departmentModel
from utils import function
from utils.yandex_disk import YandexDisk


### Информация о заказах ###

@dp.message_handler(Text(equals=["Отделы", "/departments"]), user_id=config.ADMINS)
async def show_orders(message: types.Message):
    departments = departmentModel.get_all_departments()
    if departments["code"] == 200:
        text = ""
        num = 1
        for item in departments["data"]:
            text += config.adminMessage["department_info"].format(num=num, name=item["name"], tag=item["tag"],
                                                                  count_staff=len(item["staff"]))
            num += 1
        mes = config.adminMessage["departments_main"].format(text=text)
    else:
        mes = config.adminMessage["departments_missing"]
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["dinfo", "infod"])
async def show_info_order(message: types.Message):
    mes = config.adminMessage["department_missing"]
    department = departmentModel.get_department(function.check_first_tag(message.text))
    if department["code"] == 200:
        department = department["data"]
        count_staff = ""
        for staff in department["staff"]:
            user = await bot.get_chat(staff)
            count_staff += "{name} {id}\n".format(name=user.full_name, id=user.id)
        mes = config.adminMessage["department_detailed_info"].format(name=department["name"],
                                                                     tag=department["tag"],
                                                                     count_staff=count_staff)
    await message.answer(mes)


### Создзание промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["departmentAdd"])
async def start_create_code(message: types.Message, state: FSMContext):
    await DepartmentAdd.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_add_name"])


@dp.message_handler(state=DepartmentAdd.name, user_id=config.ADMINS)
async def create_code_name(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(name=message.text)
    await DepartmentAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=DepartmentAdd.tag, user_id=config.ADMINS)
async def create_code_code(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    departments = departmentModel.get_all_departments()
    if (not "@" in message.text and not "." in message.text and not "\"" in message.text) and not (
            departments["code"] == 200 and message.text in [department["tag"] for department in departments["data"]]):
        await state.update_data(tag=message.text)
        await DepartmentAdd.wait.set()
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))
    else:
        await message.answer("Недопустимые символы (@ . \") или отдел с таким тэгом уже существует",
                             reply_markup=buttons.getCustomKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=DepartmentAdd.wait)
async def waiting(message: types.Message):
    pass


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=DepartmentAdd)
async def create_code_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = ""
    if "DepartmentAdd:tag" == state_active:
        departmentModel.create_department(data.get("name"), data.get("tag"))
        YandexDisk.mkdir_department(data.get("name"))
        await state.finish()
        await call.message.edit_text("Сохранено")
        return
    elif "DepartmentAdd:name" == state_active:
        await DepartmentAdd.tag.set()
        mes = config.adminMessage["department_add_tag"]
    await function.set_state_active(state)
    await call.message.edit_text(text=mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=DepartmentAdd)
async def create_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    if "DepartmentAdd:tag" == state_active:
        await DepartmentAdd.tag.set()
    elif "DepartmentAdd:name" == state_active:
        await DepartmentAdd.name.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_repeat"])


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=DepartmentAdd)
async def create_code_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(config.adminMessage["code_add_cancel"])
    await state.finish()


### Изменение промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["departmentEdit"])
async def start_edit_code(message: types.Message, state: FSMContext):
    mes, keyboard = menu_edit_department(-1, tag=function.check_first_tag(message.text))
    await message.answer(mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="department_name"), user_id=config.ADMINS)
async def edit_code_name_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await DepartmentEdit.name.set()
    await state.update_data(departmentEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["department_add_name"],
                                 reply_markup=buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="department_tag"), user_id=config.ADMINS)
async def edit_code_code_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await DepartmentEdit.tag.set()
    await state.update_data(departmentEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["department_add_tag"],
                                 reply_markup=buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="department_add_user"), user_id=config.ADMINS)
async def edit_code_code_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await DepartmentEdit.add_user.set()
    await state.update_data(departmentEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["department_add_user"],
                                 reply_markup=buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="department_del_user"), user_id=config.ADMINS)
async def edit_code_code_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await DepartmentEdit.del_user.set()
    await state.update_data(departmentEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["department_del_user"],
                                 reply_markup=buttons.getCustomKeyboard(cancel="Назад"))


@dp.callback_query_handler(action_callback.filter(what_action="department_delete"), user_id=config.ADMINS)
async def edit_code_delete_start(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await DepartmentEdit.delete.set()
    await state.update_data(departmentEditID=callback_data.get("id"))
    await function.set_state_active(state)
    await call.message.edit_text("Удалить отдел?", reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=DepartmentEdit.add_user, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        try:
            user = await bot.get_chat(message.text)
            await state.update_data(add_user=message.text)
            await message.answer(user.full_name + "\n" + config.adminMessage["code_add_confirmation"],
                                 reply_markup=buttons.getConfirmationKeyboard())
        except:
            await message.answer("Такой пользователь не существует.",
                                 reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))
    else:
        await message.answer("Вы ввели не число, повторите", reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.del_user, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        id = int(message.text)
        department = departmentModel.get_department_id(data.get("departmentEditID"))
        if department["code"] == 200 and id in department["data"]["staff"]:
            await state.update_data(del_user=id)
            await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                                 reply_markup=buttons.getConfirmationKeyboard())
        else:
            await message.answer("Данного пользователя и так нет в отделе)",
                                 reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))
    else:
        await message.answer("Вы ввели не число, повторите", reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.name, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(name=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=DepartmentEdit.tag, user_id=config.ADMINS)
async def edit_code_code(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    departments = departmentModel.get_all_departments()
    if (not "@" in message.text and not "." in message.text and not "\"" in message.text) and not (
            departments["code"] == 200 and message.text in [department["tag"] for department in departments["data"]]):
        await state.update_data(tag=message.text)
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer("Недопустимые символы (@ . \") или отдел с таким тэгом уже существует",
                             reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=DepartmentEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    department = departmentModel.get_department_id(data.get("departmentEditID"))
    if not department["code"] == 200:
        await state.finish()
        await call.message.edit_text(config.adminMessage["department_missing"])
        return
    department = department["data"]
    if "DepartmentEdit:delete" == state_active:
        departmentModel.delete_department(department["id"])
        await state.finish()
        await call.message.edit_text(text=config.adminMessage["department_del_yes"])
        return

    if "DepartmentEdit:name" == state_active:
        departmentModel.update_department(department["id"], data.get("name"), department["tag"])
    elif "DepartmentEdit:tag" == state_active:
        departmentModel.update_department(department["id"], department["name"], data.get("tag"))
    elif "DepartmentEdit:add_user" == state_active:
        departmentModel.add_staff(department["id"], data.get("add_user"))
    elif "DepartmentEdit:del_user" == state_active:
        departmentModel.del_staff(department["id"], data.get("del_user"))

    mes, keyboard = menu_edit_department(data.get("departmentEditID"))
    await state.finish()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=DepartmentEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes, keyboard = menu_edit_department(data.get("departmentEditID"))
    await state.finish()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=DepartmentEdit)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes, keyboard = menu_edit_department(data.get("departmentEditID"))
    await state.finish()
    await call.message.edit_text(text=mes, reply_markup=keyboard)


def menu_edit_department(departmentID, tag=None):
    if not tag is None:
        department = departmentModel.get_department(tag)
    else:
        department = departmentModel.get_department_id(departmentID)
    if department["code"] == 200:
        department = department["data"]
        return [config.adminMessage["department_edit"].format(name=department["name"],
                                                              tag=department["tag"]),
                buttons.getActionKeyboard(department["id"], department_name="Название", department_tag="Тэг",
                                          department_add_user="Добавить сотрудника",
                                          department_del_user="Удалить сотрудника", department_delete="Удалить отдел")]
    else:
        return [config.adminMessage["department_missing"], None]
