import math

from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.inline import buttons
from keyboards.inline.callback_datas import numbering_callback
from loader import dp, bot
from utils.db_api.models import departmentModel, tasksModel, tasksCompletesModel, orderModel
from utils import function


@dp.message_handler(user_id=config.ADMINS, commands=["set_task"])
async def start_edit_code(message: types.Message, state: FSMContext):
    mes = "В работе"
    tags = function.check_all_tag(message.text)
    staff = {}
    for tag in tags:
        tag_temporary = tag.split(".")[0] if "." in tag else tag
        department = departmentModel.get_department(tag_temporary)
        if department:
            try:
                staff_temporary = [department.staff[int(tag.split(".")[1]) - 1]] if "." in tag else department.staff
                if tag_temporary in staff.keys():
                    staff[tag_temporary] = sorted(staff[tag_temporary] + staff_temporary)
                else:
                    staff[tag_temporary] = staff_temporary
            except:
                pass
        else:
            await message.answer(text=config.adminMessage["department_missing"])
            return
    orderID = function.check_number(message.text)
    text = function.string_handler(function.check_text(message.text))
    order = orderModel.get_order(orderID)
    if orderID is None or not order:
        await message.answer("Вы не указали номер заказа или указали на несуществующий заказ")
        return
    elif not order.active:
        await message.answer("Заказ уже закрыт")
        return
    elif not staff:
        await message.answer("Вы неверно указали сотрудников")
        return

    for departmentTag in staff:
        for userID in staff[departmentTag]:
            tasksModel.del_task_duplicate(userID, departmentTag, orderID)
            tasksCompletesModel.del_task_duplicate(userID, departmentTag, orderID)
            await bot.send_message(chat_id=userID, text=config.adminMessage["new_task_staff"])
        tasksModel.create_task(orderID, staff[departmentTag], departmentTag, text)
    await message.answer(mes)


@dp.message_handler(user_id=config.ADMINS, commands=["task_listA"])
async def close_order(message: types.Message, state: FSMContext):
    mes, keyboard = await menu_task_list(0)
    await message.answer(text=mes, reply_markup=keyboard)


@dp.callback_query_handler(numbering_callback.filter(what_action="TasksNumbering"), user_id=config.ADMINS)
async def close_order_button(call: types.CallbackQuery, callback_data: dict):
    mes, keyboard = await menu_task_list(int(callback_data["number"]))
    try:
        await call.message.edit_text(text=mes, reply_markup=keyboard)
    except:
        await call.answer(cache_time=1)


@dp.message_handler(user_id=config.ADMINS, commands=["all_result"])
async def close_order(message: types.Message, state: FSMContext):
    result = tasksCompletesModel.get_orderID_tasks_completes(function.checkID(message.text))
    mes = config.adminMessage["task_result_missing"]
    if result:
        text = ""
        documents = []
        for number, task in enumerate(result):
            user = await bot.get_chat(task.userID)
            text += config.adminMessage["task_result_info"].format(number=number + 1, department=task.departmentTag,
                                                                   user=user.full_name,
                                                                   userID=task.userID)
            documents += task.document
        for document in documents:
            await message.answer_document(document=document)
        mes = config.adminMessage["task_result_main"].format(text=text)
    await message.answer(mes)


async def menu_task_list(page):
    mes = config.adminMessage["task_list_missing"]
    keyboard = None
    tasks = tasksModel.get_tasks(page, config.max_size_task)
    tasks_count = tasksModel.get_tasks_count()
    if tasks:
        text = ""
        tasksOrder = {}
        for task in tasks:
            tasksOrder[task.orderID] = tasksOrder[task.orderID] + len(task.staff) if task.orderID in tasksOrder.keys() else len(
                task.staff)
        for order, staff in tasksOrder.items():
            text += config.adminMessage["task_list_info"].format(orderID=order, staff=staff)
        mes = config.adminMessage["task_list_main"].format(text=text)
        keyboard = await buttons.getNumbering(math.ceil(tasks_count / config.max_size_task), "TasksNumbering")
    return mes, keyboard
