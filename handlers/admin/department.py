from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp, bot
from states.admin_close_order import AdminCloseOrder
from states.admin_create_department import DepartmentAdd
from states.admin_edit_department import DepartmentEdit
from states.admin_mes_order import AdminMesOrder
from utils.db_api.models import departmentModel
from utils import function


### Информация о заказах ###

@dp.message_handler(user_id=config.ADMINS, commands=["departments"])
async def show_orders(message: types.Message):
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
              "Ноябрь", "Декабрь"]
    departments = departmentModel.get_all_departments()
    if departments["success"]:
        text = ""
        num = 1
        for item in departments["data"]:
            text += config.adminMessage["department_info"].format(num=num, name=item["name"], tag=item["tag"],
                                                                  count_staff=len(item["staff"]))
            num += 1
        mes = config.adminMessage["departments_main"].format(text=text)
    else:
        mes = config.adminMessage["departments_missing"]
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["dinfo", "infod"])
async def show_info_order(message: types.Message):
    mes = config.adminMessage["department_missing"]
    department = departmentModel.get_department(function.check_first_tag(message.text))
    if department["success"]:
        count_staff = ""
        for staff in department["staff"]:
            user = await bot.get_chat(staff)
            count_staff += "{name} {id}\n".format(name=user.full_name, id=user.id)
        mes = config.adminMessage["department_detailed_info"].format(name=department["name"],
                                                                     tag=department["tag"],
                                                                     count_staff=count_staff)
    await message.answer(mes, reply_markup=menu)


### Создзание промокода ###

@dp.message_handler(user_id=config.ADMINS, commands=["departmentAdd"])
async def start_create_code(message: types.Message, state: FSMContext):
    await DepartmentAdd.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_add_name"], reply_markup=menu)


@dp.message_handler(state=DepartmentAdd.name, user_id=config.ADMINS)
async def create_code_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await DepartmentAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))


@dp.message_handler(state=DepartmentAdd.tag, user_id=config.ADMINS)
async def create_code_code(message: types.Message, state: FSMContext):
    await state.update_data(tag=message.text)
    await DepartmentAdd.wait.set()
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить создание"))


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
    mes = config.adminMessage["department_missing"]
    department = departmentModel.get_department(function.check_first_tag(message.text))
    if department["success"]:
        await state.update_data(departmentEditID=department["id"])
        mes = config.adminMessage["department_edit"].format(name=department["name"],
                                                            tag=department["tag"])
        await DepartmentEdit.zero.set()
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["name"])
async def edit_code_name_start(message: types.Message, state: FSMContext):
    await DepartmentEdit.name.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_add_name"],
                         reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["tag"])
async def edit_code_code_start(message: types.Message, state: FSMContext):
    await DepartmentEdit.tag.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_add_tag"],
                         reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["add_user"])
async def edit_code_code_start(message: types.Message, state: FSMContext):
    await DepartmentEdit.add_user.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_add_user"],
                         reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["del_user"])
async def edit_code_code_start(message: types.Message, state: FSMContext):
    await DepartmentEdit.del_user.set()
    await function.set_state_active(state)
    await message.answer(config.adminMessage["department_del_user"],
                         reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["delete"])
async def edit_code_delete_start(message: types.Message, state: FSMContext):
    await DepartmentEdit.delete.set()
    await function.set_state_active(state)
    await message.answer("Удалить отдел?", reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=DepartmentEdit.zero, user_id=config.ADMINS, commands=["back"])
async def edit_code_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(config.adminMessage["department_edit_back"])


@dp.message_handler(state=DepartmentEdit.add_user, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(add_user=message.text)
        await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                             reply_markup=buttons.getConfirmationKeyboard())
    else:
        await message.answer("Вы ввели не число, повторите", reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.del_user, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        id = int(message.text)
        department = departmentModel.get_department_id(data.get("departmentEditID"))
        if department["success"] and id in department["staff"]:
            await state.update_data(del_user=id)
            await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                                 reply_markup=buttons.getConfirmationKeyboard())
        else:
            await message.answer("Данного пользователя и так нет в отделе)", reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))
    else:
        await message.answer("Вы ввели не число, повторите", reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.message_handler(state=DepartmentEdit.name, user_id=config.ADMINS)
async def edit_code_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.message_handler(state=DepartmentEdit.tag, user_id=config.ADMINS)
async def edit_code_code(message: types.Message, state: FSMContext):
    await state.update_data(tag=message.text)
    await message.answer(message.text + "\n" + config.adminMessage["code_add_confirmation"],
                         reply_markup=buttons.getConfirmationKeyboard())


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=DepartmentEdit)
async def edit_product_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    department = departmentModel.get_department_id(data.get("departmentEditID"))
    if not department["success"]:
        await state.finish()
        await call.message.edit_text(config.adminMessage["department_missing"])
        return

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
    await DepartmentEdit.zero.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["department_edit"].format(name=department["name"],
                                                                               tag=department["tag"]))


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=DepartmentEdit)
async def edit_code_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    if "DepartmentEdit:delete" == state_active:
        await call.message.edit_text(config.adminMessage["department_del_no"])
        await DepartmentEdit.zero.set()
        return
    elif "DepartmentEdit:name" == state_active:
        await DepartmentEdit.name.set()
    elif "DepartmentEdit:tag" == state_active:
        await DepartmentEdit.tag.set()
    await function.set_state_active(state)
    await call.message.edit_text(config.adminMessage["code_add_repeat"],
                                 reply_markup=buttons.getCustomKeyboard(cancel="Отменить"))


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=DepartmentEdit)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery):
    await DepartmentEdit.zero.set()
    await call.message.edit_text(config.adminMessage["department_edit_no"])
