async def set_state_active(state):
    async with state.proxy() as data:
        data["state_active"] = await state.get_state()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1


def check_first_tag(mes):
    try:
        return mes.split(' ')[1].split('@')[1]
    except:
        return "None"
