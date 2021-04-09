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
from utils.telegram_files import TelegramFiles


@dp.message_handler(commands=["task_list"])
async def close_order(message: types.Message):
    staffs = departmentModel.get_all_staffs()
    if message.from_user.id in staffs:
        mes, keyboard = await menu_tasks_list(message.from_user.id)
        await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskOrder"))
async def close_order(call: types.CallbackQuery, callback_data: dict):
    staffs = departmentModel.get_all_staffs()
    if call.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        keyboard = None
        task = tasksModel.get_task(callback_data.get("id"))
        if not task:
            await call.message.edit_text(text="Задача отсутствует")
            return
        order = orderModel.get_order(task.orderID)
        if order and check_tasks(call.from_user.id, order.id):
            mes = config.departmentMessage["task_info"].format(orderID=order.id, price=order.price,
                                                               description=order.description,
                                                               descriptionA=task.message)
            if task.departmentTag == config.department_courier_tag:
                keyboard = await buttons.getActionKeyboard(task.id,
                                                           departmentTaskDelivery="Начать доставку",
                                                           departmentTaskCancel="Назад")
            else:
                keyboard = await buttons.getActionKeyboard(task.id, departmentTaskSend="Сдать работу",
                                                           departmentTaskCancel="Назад")
            if len(order.document) == 1:
                await call.message.delete()
                await call.message.answer_document(caption=mes, document=order.document[0], reply_markup=keyboard)
                return
            elif len(order.document) > 1:
                await call.message.delete()
                for document in order.document:
                    await call.message.answer_document(document=document)
        await call.message.edit_text(mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskSend"))
async def send_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    staffs = departmentModel.get_all_staffs()
    if call.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        keyboard = None
        task = tasksModel.get_task(callback_data.get("id"))
        if not task:
            await call.message.delete()
            await call.message.answer(text="Задача отсутствует")
            return
        order = orderModel.get_order(task.orderID)
        if order:
            keyboard = await buttons.getCustomKeyboard(cancel="Отменить")
            mes = config.departmentMessage["task_add_comment"]
            await state.update_data(orderID=order.id, taskID=task.id)
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
                         reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить"))


@dp.message_handler(state=TaskComplete.wait)
async def waiting(message: types.Message):
    pass


@dp.message_handler(state=TaskComplete.document, content_types=types.ContentType.DOCUMENT)
async def message_add_doc(message: types.Message, state: FSMContext):
    if TelegramFiles.document_size(message.document.file_size):
        await state.update_data(document=message.document)
        await TaskComplete.wait.set()
        await message.answer(config.message["document_confirmation"].format(
            text="{name} {size}мб\n".format(name=message.document.file_name, size=round(message.document.file_size/1024/1024, 3))),
            reply_markup=await buttons.getConfirmationKeyboard(cancel="Отменить"))
    else:
        await message.answer(config.message["document_confirmation_size"].format(
            text="{name} {size}мб\n".format(name=message.document.file_name, size=round(message.document.file_size/1024/1024, 3))),
            reply_markup=await buttons.getCustomKeyboard(cancel="Отменить"))


@dp.callback_query_handler(confirmation_callback.filter(bool="Yes"), state=TaskComplete)
async def adding_comment_or_promoCode_yes(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mes = ""
    keyboard = None
    state_active = data.get("state_active")
    if "TaskComplete:document" == state_active:
        task = tasksModel.get_task(data.get("taskID"))
        userDepartment = ""
        userDepartmentName = ""
        if task:
            userDepartment = task.departmentTag
            department = departmentModel.get_department(userDepartment)
            userDepartmentName = department.name if department else ""
        else:
            await call.message.edit_text(
                text="Произашла ошибка, невозможно отправить данную работу, обратитесь к администрации.")
            return
        tasksCompletesModel.create_task_complete(call.from_user.id, data.get("orderID"), userDepartment,
                                                 data.get("description"), [data.get("document").file_id])
        tasksModel.del_task_duplicate(call.from_user.id, userDepartment, data.get("orderID"))
        # Сохранение файла на диске #
        await save_file(data.get("document"), call.from_user.id, data.get("orderID"), userDepartmentName)
        # ---------------------- #
        await state.finish()
        mes, keyboard = await menu_tasks_list(call.from_user.id)
        await call.message.edit_text(text=mes, reply_markup=keyboard)
        await call.message.answer(text=config.departmentMessage["task_send"])
        return
    elif "TaskComplete:description" == state_active:
        await TaskComplete.document.set()
        mes = config.departmentMessage["task_add_document"]
        keyboard = await buttons.getCustomKeyboard(cancel="Отменить")
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
    await call.message.edit_text(text=mes, reply_markup=await buttons.getCustomKeyboard(cancel="Отменить"))


@dp.callback_query_handler(confirmation_callback.filter(bool="cancel"), state=TaskComplete)
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    mes, keyboard = await menu_tasks_list(call.from_user.id)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskDelivery"))
async def send_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    orderId = tasksModel.get_task(callback_data.get("id")).orderID
    user = await bot.get_chat(orderModel.get_order(orderId).userID)
    tasksModel.del_task_duplicate(call.from_user.id, config.department_courier_tag, orderId)
    await call.message.delete()
    await call.message.answer(text=config.departmentMessage["delivery_send"].format(user.mention))


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskCancel"))
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    mes, keyboard = await menu_tasks_list(call.from_user.id)
    if call.message.document is None:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    else:
        await call.message.delete()
        await call.message.answer(text=mes, reply_markup=keyboard)


def check_tasks(staffID, orderID):
    response = tasksModel.get_user_tasks(staffID)
    return response and orderID in [task.orderID for task in response]


async def menu_tasks_list(userID):
    tasks = tasksModel.get_user_tasks(userID)
    mes = config.departmentMessage["task_list_missing"]
    keyboard = None
    keyboard_info = {}
    if tasks:
        mes = config.departmentMessage["task_main"]
        for task in tasks:
            keyboard_info[config.departmentMessage["task_button"].format(task.orderID, task.departmentTag)] = task.id
        keyboard = await buttons.getAuxiliaryOrdersKeyboard("departmentTaskOrder", keyboard_info)
    return [mes, keyboard]


async def save_file(document, userID, orderID, userDepartmentName):
    path = f"{os.path.dirname(os.path.abspath(__file__))}/../../documents/{userDepartmentName}/{userID}/{orderID}"
    if not os.path.exists(path):
        os.makedirs(path)
    file_info = await bot.get_file(
        file_id=document.file_id)
    file_extension = os.path.splitext(file_info.file_path)[1]
    file_name = document.file_name.split(".")[0]
    file = await bot.download_file(file_path=file_info.file_path)
    with open(
            f'{path}/{file_name}{file_extension}',
            'wb') as new_file:
        new_file.write(file.read())
