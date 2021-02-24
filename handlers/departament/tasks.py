from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback, action_callback
from loader import dp
from states.staff_task_complete import TaskComplete
from utils.db_api.models import departmentModel, tasksModel, tasksCompletesModel, orderModel
from utils import function


@dp.message_handler(commands=["task_list"])
async def close_order(message: types.Message):
    staffs = departmentModel.get_all_staffs()
    if message.from_user.id in staffs:
        mes, keyboard = menu_edit_promoCode(message.from_user.id)
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
            keyboard = buttons.getActionKeyboard(order["id"], departmentTaskSend="Сдать работу",
                                                 departmentTaskCancel="Назад")
            form = "Номер заказа <b>{orderID}</b>\nКоментарий к заказу: {description}\nКоментарий от админа: {descriptionA}"
            mes = form.format(orderID=order["id"], price=order["price"],
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
        order = orderModel.get_order(callback_data.get("id"))
        if order["code"] == 200 and check_tasks(call.from_user.id, order["data"]["id"]):
            keyboard = buttons.getCustomKeyboard(cancel="Отменить")
            mes = "Напишите коментарий к работе:"
            await state.update_data(orderID=order["data"]["id"])
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
    await call.answer(cache_time=2)
    data = await state.get_data()
    mes = ""
    keyboard = None
    state_active = data.get("state_active")
    if "TaskComplete:document" == state_active:
        response = departmentModel.get_all_departments()
        userDepartment = ""
        if response["code"] == 200:
            for department in response["data"]:
                if call.from_user.id in department["staff"]:
                    userDepartment = department["tag"]
                    break
        tasksCompletesModel.create_task_complete(call.from_user.id, data.get("orderID"), userDepartment,
                                                 data.get("description"), [data.get("document").file_id])
        tasksModel.del_task_duplicate(call.from_user.id, userDepartment, data.get("orderID"))
        await state.finish()
        mes, keyboard = menu_edit_promoCode(call.from_user.id)
        await call.message.edit_text(text=mes, reply_markup=keyboard)
        await call.message.answer(text="Ответ отрпавлен")
        return
    elif "TaskComplete:description" == state_active:
        await TaskComplete.document.set()
        mes = "Прикрепите документ или архив с работой"
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
    mes, keyboard = menu_edit_promoCode(call.from_user.id)
    await call.message.edit_text(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(action_callback.filter(what_action="departmentTaskCancel"))
async def adding_comment_or_promoCode_cancel(call: types.CallbackQuery, state: FSMContext):
    mes, keyboard = menu_edit_promoCode(call.from_user.id)
    if call.message.document is None:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    else:
        await call.message.delete()
        await call.message.answer(text=mes, reply_markup=keyboard)


def check_tasks(staffID, orderID):
    response = tasksModel.get_user_tasks(staffID)
    return response["code"] == 200 and orderID in [task["orderID"] for task in response["data"]]


def menu_edit_promoCode(userID):
    tasks = tasksModel.get_user_tasks(userID)
    mes = "У вас нет задач"
    keyboard = None
    keyboard_info = {}
    if tasks["code"] == 200:
        mes = "Список ваших задач:\n"
        for number, task in enumerate(tasks["data"]):
            keyboard_info["Заказ номер {}".format(task["orderID"])] = task["id"]
        keyboard = buttons.getAuxiliaryOrdersKeyboard("departmentTaskOrder", keyboard_info)
    return [mes, keyboard]
