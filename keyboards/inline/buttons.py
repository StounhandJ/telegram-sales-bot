from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import action_callback, setting_callback, confirmation_callback, \
    type_work_callback, numbering_callback
from data import config


async def getSellWorkKeyboard(type_work):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data=setting_callback.new(command="exit", type="zero")),
            InlineKeyboardButton(text="Далее", callback_data=setting_callback.new(command="continue", type=type_work))
        ]
    ])


async def getConfirmationKeyboard(**kwargs):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=confirmation_callback.new(bool="Yes")),
            InlineKeyboardButton(text="Нет", callback_data=confirmation_callback.new(bool="No"))
        ]])
    for arg, text in kwargs.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=confirmation_callback.new(bool=arg)))
    return keyboard


async def getCustomKeyboard(**kwargs):
    keyboard = InlineKeyboardMarkup()
    for arg, text in kwargs.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=confirmation_callback.new(bool=arg)))
    return keyboard


async def getActionKeyboard(id, **kwargs):
    keyboard = InlineKeyboardMarkup()
    for arg, text in kwargs.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=action_callback.new(what_action=arg, id=id)))
    return keyboard


async def getAuxiliaryOrdersKeyboard(action, orders):
    """
    orders = {"id": orderID,
              "text": Текст кнопки}
    """
    keyboard = InlineKeyboardMarkup()
    for text, id in orders.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=action_callback.new(what_action=action, id=id)))
    return keyboard


async def getTypeWorkKeyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Курсовая работа", callback_data=type_work_callback.new(work="Курсовая")),
            InlineKeyboardButton(text="Дипломная работа", callback_data=type_work_callback.new(work="Дипломная"))
        ]
    ])
    keyboard.add(InlineKeyboardButton(text="Другие работы", callback_data=type_work_callback.new(work="other_works")))
    return keyboard


async def getOtherWorks():
    keyboard = InlineKeyboardMarkup(row_width=3)
    for work in config.works:
        if work != "Курсовая" and work != "Дипломная":
            keyboard.row(
                InlineKeyboardButton(text=work, callback_data=type_work_callback.new(work=work)))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data=type_work_callback.new(work="back")))
    return keyboard


async def getNumbering(count, action):
    if count < 2:
        return None
    buttons = []
    for number in range(0, count):
        if len(buttons) == number // config.row_numbering_keyboard: buttons.append([])
        buttons[number // config.row_numbering_keyboard].append(InlineKeyboardButton(text=str(number+1), callback_data=numbering_callback.new(what_action=action, number=number)))
    keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=buttons)
    return keyboard
