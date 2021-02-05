from aiogram.dispatcher.filters.state import StatesGroup, State


class CodeAdd(StatesGroup):
    name = State()
    code = State()
    percent = State()
    discount = State()
