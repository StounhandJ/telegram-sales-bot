from aiogram.dispatcher.filters.state import StatesGroup, State


class DepartmentEdit(StatesGroup):
    zero = State()
    name = State()
    tag = State()
    add_user = State()
    del_user = State()
    delete = State()
