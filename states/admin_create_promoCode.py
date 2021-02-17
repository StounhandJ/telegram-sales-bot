from aiogram.dispatcher.filters.state import StatesGroup, State


class CodeAdd(StatesGroup):
    name = State()
    code = State()
    limitationUse = State()
    count = State()
    percent = State()
    discount = State()
    wait = State()
