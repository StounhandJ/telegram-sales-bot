from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from loader import dp, bot
from utils.db_api.models import departmentModel, tasksModel, tasksCompletesModel, orderModel
from utils import function


@dp.message_handler(user_id=config.ADMINS, commands=["set_task"])
async def start_edit_code(message: types.Message, state: FSMContext):
    mes = "В работе"
    tags = function.check_all_tag(message.text)
    staff = []
    for tag in tags:
        department = departmentModel.get_department(tag.split(".")[0] if "." in tag else tag)
        if department["code"] == 200:
            try:
                staff_temporary = [department["data"]["staff"][int(tag.split(".")[1]) - 1]] if "." in tag else \
                    department["data"][
                        "staff"]
                staff = sorted(staff + staff_temporary)
            except:
                pass
    orderID = function.check_number(message.text)
    text = function.check_text(message.text)
    if orderID is None or orderModel.get_order(orderID)["code"] != 200:
        await message.answer("Вы не указали номер заказа или указали на несуществующий заказ", reply_markup=menu)
        return
    elif not staff:
        await message.answer("Вы неверно указали сотрудников", reply_markup=menu)
        return

    for userID in staff:
        tasksModel.del_task_duplicate(userID, orderID)
        tasksCompletesModel.del_task_duplicate(userID, orderID)
    tasksModel.create_task(orderID, staff, text)
    await message.answer(mes, reply_markup=menu)


@dp.message_handler(user_id=config.ADMINS, commands=["task_list"])
async def close_order(message: types.Message, state: FSMContext):
    tasks = tasksModel.get_all_tasks()
    mes_start = "Задачи не установлены"
    if tasks["code"] == 200:
        mes_start = "Задачи:\n"
        form = "Номер заказа <b>{orderID}</b>\nКоличество людей в работе: {staff}\n\n"
        tasksOrder = {}
        for task in tasks["data"]:
            tasksOrder[task["orderID"]] = tasksOrder[task["orderID"]] + len(task["staff"]) if task[
                                                                                                  "orderID"] in tasksOrder.keys() else len(
                task["staff"])
        for order, staff in tasksOrder.items():
            mes_start += form.format(orderID=order, staff=staff)
        mes_start += "/set_task staff orderID mes\n/all_result orderID"
    await message.answer(mes_start)


@dp.message_handler(user_id=config.ADMINS, commands=["all_result"])
async def close_order(message: types.Message, state: FSMContext):
    result = tasksCompletesModel.get_orderID_tasks_completes(function.checkID(message.text))
    mes_start = "Результатов по данной работе нет"
    if result["code"] == 200:
        mes_start = "Результаты:\n"
        form = "{number}. @{department} {user} ({userID})\n\n"
        documents = []
        for number, task in enumerate(result["data"]):
            user = await bot.get_chat(task["userID"])
            mes_start += form.format(number=number + 1, department=task["departmentTAG"], user=user.full_name, userID=task["userID"])
            documents += task["document"]
        for document in documents:
            await message.answer_document(document=document)
    await message.answer(mes_start)
