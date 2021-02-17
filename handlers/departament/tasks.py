from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from keyboards.inline import buttons
from keyboards.inline.callback_datas import confirmation_callback
from loader import dp
from states.staff_task_complete import TaskComplete
from utils.db_api.models import departmentModel, tasksModel, tasksCompletesModel, orderModel
from utils import function


@dp.message_handler(commands=["task_list"])
async def close_order(message: types.Message, state: FSMContext):
    staffs = departmentModel.get_all_staffs()

    if message.from_user.id in staffs:
        tasks = tasksModel.get_user_tasks(message.from_user.id)
        mes_start = "У вас нет задач"
        if tasks["code"] == 200:
            mes_start = "Список ваших задач:\n"
            form = "{number}. \nНомер заказа <b>{orderID}</b>\nСообщение для вас: {mes}\n\n"
            for number, task in enumerate(tasks["data"]):
                mes_start += form.format(number=number + 1, orderID=task["orderID"], mes=task["message"])
            mes_start += "/ordinfo orderID - информация о заказе\n/task_complete orderID - Сдать выполненую работу"
        await message.answer(mes_start)


@dp.message_handler(commands=["ordinfo"])
async def close_order(message: types.Message, state: FSMContext):
    staffs = departmentModel.get_all_staffs()

    if message.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        order = orderModel.get_order(function.checkID(message.text))
        if order["code"] == 200 and check_tasks(message.from_user.id, order["data"]["id"]):
            order = order["data"]
            form = "Номер заказа <b>{orderID}</b>\nКоментарий к заказу: {description}\n"
            mes = form.format(orderID=order["id"], price=order["price"],
                              description=order["description"],
                              date=datetime.utcfromtimestamp(
                                  order["date"]).strftime('%Y-%m-%d %H:%M:%S'))
            if len(order["document"]) == 1:
                await message.answer_document(caption=mes, document=order["document"][0])
                return
            elif len(order["document"]) > 1:
                for document in order["document"]:
                    await message.answer_document(document=document)
        await message.answer(mes, reply_markup=menu)


@dp.message_handler(commands=["task_complete"])
async def close_order(message: types.Message, state: FSMContext):
    staffs = departmentModel.get_all_staffs()
    if message.from_user.id in staffs:
        mes = config.adminMessage["order_missing"]
        keyboard = None
        order = orderModel.get_order(function.checkID(message.text))
        if order["code"] == 200 and check_tasks(message.from_user.id, order["data"]["id"]):
            keyboard = buttons.getCustomKeyboard(cancel="Отменить")
            mes = "Напишите коментарий к работе:"
            await state.update_data(orderID=order["data"]["id"])
            await TaskComplete.description.set()
            await function.set_state_active(state)
        await message.answer(mes, reply_markup=keyboard)


@dp.message_handler(state=TaskComplete.description)
async def adding_comment(message: types.Message, state: FSMContext):
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
    state_active = data.get("state_active")
    keyboard = None
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
        tasksModel.del_task_duplicate(call.from_user.id, data.get("orderID"))
        await state.finish()
        await call.message.edit_text(text="Ответ отправлен")
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
    await call.message.edit_text("Отправка результата рыботы отменена")


def check_tasks(staffID, orderID):
    response = tasksModel.get_user_tasks(staffID)
    return response["code"] == 200 and orderID in [task["orderID"] for task in response["data"]]
