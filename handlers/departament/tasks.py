import os

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback
from loader import dp, bot
from states.staff_task_complete import TaskComplete
from utils.db_api.models import departmentModel, tasksModel, tasksCompletesModel, orderModel
from utils import function


@dp.message_handler(commands=["task_list"])
async def close_order(message: types.Message):
    staffs = departmentModel.get_all_staffs()
    if message.from_user.id in staffs:
        mes, keyboard = menu_tasks_list(message.from_user.id)
        await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskOrder"))
async def close_order(call: types.CallbackQuery, callback_data: dict):
    staffs = departmentModel.get_all_staffs()
    if call.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        keyboard = None
        task = tasksModel.get_task(callback_data.get("id"))
        if task["code"] != 200:
            await call.message.edit_text(text="Задача отсутствует")
            return
        order = orderModel.get_order(task["data"]["orderID"])
        if order["code"] == 200 and check_tasks(call.from_user.id, order["data"]["id"]):
            order = order["data"]
            keyboard = buttons.getActionKeyboard(task["data"]["id"], departmentTaskSend="Сдать работу",
                                                 departmentTaskCancel="Назад")
            mes = config.departmentMessage["task_info"].format(orderID=order["id"], price=order["price"],
                                                               description=order["description"],
                                                               descriptionA=task["data"]["message"])
            if len(order["document"]) == 1:
                await call.message.delete()
                await call.message.answer_document(caption=mes, document=order["document"][0], reply_markup=keyboard)
                return
            elif len(order["document"]) > 1:
                await call.message.delete()
                for document in order["document"]:
                    await call.message.answer_document(document=document)
        await call.message.edit_text(mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskSend"))
async def close_order(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    staffs = departmentModel.get_all_staffs()
    if call.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        keyboard = None
        task = tasksModel.get_task(callback_data.get("id"))
        if task["code"] != 200:
            await call.message.edit_text(text="Задача отсутствует")
            return
        order = orderModel.get_order(task["data"]["orderID"])
        if order["code"] == 200:
            keyboard = buttons.getCustomKeyboard(cancel="Отменить")
            mes = config.departmentMessage["task_add_comment"]
            await state.update_data(orderID=order["data"]["id"], taskID=task["data"]["id"])
            await TaskComplete.description.set()
            await function.set_state_active(state)

        if call.message.document is None:
            await call.message.edit_text(text=mes, reply_markup=keyboard)
        else:
            await call.message.delete()
            await call.message.answer(text=mes, reply_markup=keyboard)


@dp.message_handler(state=TaskComplete.description)
async def adding_comment(message: types.Message, state: FSMContext):
    message.text = function.string_handler(message.text)
    await state.update_data(description=message.text)
    await TaskComplete.wait.set()
    await message.answer(config.message["comment_confirmation"].format(text=message.text),
                         reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить"))


@dp.message_handler(state=TaskComplete.wait)
async def waiting(message: types.Message):
    pass


@dp.message_handler(state=TaskComplete.document, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document)
    await TaskComplete.wait.set()
    await message.answer(config.message["document_confirmation"].format(
        text="{name} {size}кб\n".format(name=message.document.file_name, size=message.document.file_size)),
        reply_markup=buttons.getConfirmationKeyboard(cancel="Отменить"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=TaskComplete)
async def adding_comment_or_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = ""
    keyboard = None
    state_active = data.get("state_active")
    if "TaskComplete:document" == state_active:
        response = tasksModel.get_task(data.get("taskID"))
        userDepartment = ""
        userDepartmentName = ""
        if response["code"] == 200:
            userDepartment = response["data"]["departmentTag"]
            department = departmentModel.get_department(userDepartment)
            userDepartmentName = department["data"]["name"] if department["code"] == 200 else ""
        else:
            await call.message.edit_text(text="Произашла ошибка, невозможно отправить данную работу, обратитесь к администрации.")
            return
        tasksCompletesModel.create_task_complete(call.from_user.id, data.get("orderID"), userDepartment,
                                                 data.get("description"), [data.get("document").file_id])
        tasksModel.del_task_duplicate(call.from_user.id, userDepartment, data.get("orderID"))
        # Сохранение файла на диске #
        if not os.path.exists(f"documents/{userDepartmentName}/{call.from_user.id}/{data.get('orderID')}"):
            os.makedirs(f"documents/{userDepartmentName}/{call.from_user.id}/{data.get('orderID')}")
        file_info = await bot.get_file(
            file_id=data.get("document").file_id)
        file_extension = os.path.splitext(file_info.file_path)[1]
        file_name = data.get("document").file_name.split(".")[0]
        file = await bot.download_file(file_path=file_info.file_path)
        with open(f'documents/{userDepartmentName}/{call.from_user.id}/{data.get("orderID")}/{file_name}{file_extension}', 'wb') as new_file:
            new_file.write(file.read())
        # ---------------------- #
        await state.finish()
        mes, keyboard = menu_tasks_list(call.from_user.id)
        await call.message.edit_text(text=mes, reply_markup=keyboard)
        await call.message.answer(text=config.departmentMessage["task_send"])
        return
    elif "TaskComplete:description" == state_active:
        await TaskComplete.document.set()
        mes = config.departmentMessage["task_add_document"]
        keyboard = buttons.getCustomKeyboard(cancel="Отменить")
    await function.set_state_active(state)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(confirmation_callback.filter(bool="No"), state=TaskComplete)
async def adding_comment_or_promoCode_no(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_active = data.get("state_active")
    mes = config.message["comment_confirmation_no"]
    if "TaskComplete:document" == state_active:
        await TaskComplete.document.set()
    elif "TaskComplete:description" == state_active:
        await TaskComplete.description.set()
    await function.set_state_active(state)
    await call.message.edit_text(text=mes)


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=TaskComplete)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    mes, keyboard = menu_tasks_list(call.from_user.id)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskCancel"))
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    mes, keyboard = menu_tasks_list(call.from_user.id)
    if call.message.document is None:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    else:
        await call.message.delete()
        await call.message.answer(text=mes, reply_markup=keyboard)


def check_tasks(staffID, orderID):
    response = tasksModel.get_user_tasks(staffID)
    return response["code"] == 200 and orderID in [task["orderID"] for task in response["data"]]


def menu_tasks_list(userID):
    tasks = tasksModel.get_user_tasks(userID)
    mes = config.departmentMessage["task_list_missing"]
    keyboard = None
    keyboard_info = {}
    if tasks["code"] == 200:
        mes = config.departmentMessage["task_main"]
        for number, task in enumerate(tasks["data"]):
            keyboard_info[config.departmentMessage["task_button"].format(task["orderID"], task["departmentTag"])] = task["id"]
        keyboard = buttons.getAuxiliaryOrdersKeyboard("departmentTaskOrder", keyboard_info)
    return [mes, keyboard]
