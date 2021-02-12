from aiogram import types
from aiogram.dispatcher import FSMContext

from data import config
from keyboards.default.menu import menu
from loader import dp
from utils.db_api.models import departmentModel, tasksModel, orderModel
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
                staff_temporary = [department["data"]["staff"][int(tag.split(".")[1])-1]]if "." in tag else department["data"][
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
    tasksModel.create_task(orderID, staff, text)
    await message.answer(mes, reply_markup=menu)
