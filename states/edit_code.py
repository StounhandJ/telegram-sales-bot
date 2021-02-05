from aiogram.dispatcher.filters.state import StatesGroup, State


class CodeEdit(StatesGroup):
    zero = State()
    name = State()
    code = State()
    percent = State()
    discount = State()
    delete = State()
