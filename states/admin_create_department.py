from aiogram.dispatcher.filters.state import StatesGroup, State


class DepartmentAdd(StatesGroup):
    name = State()
    tag = State()
    wait = State()
