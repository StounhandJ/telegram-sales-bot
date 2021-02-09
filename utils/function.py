async def set_state_active(state):
    async with state.proxy() as data:
        data["state_active"] = await state.get_state()


def checkID(mes):
    try:
        return int(mes.split(' ')[1])
    except:
        return -1