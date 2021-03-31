from utils.db_api.db import DataBase
from utils.db_api.request import request


class User:

    def __init__(self, id, telegramID, mail):
        self.id = id
        self.telegramID = telegramID
        self.mail = mail


def get_user(telegramID):
    response = request("GET", "/client", {"telegramID": telegramID})
    return User(response["data"]["id"], response["data"]["telegramID"], response["data"]["mail"])\
        if response["code"] == 200 else None


def add_user(telegramID, mail=None, payment=0):
    response = request("POST", "/client.create", {"telegramID": telegramID, "mail": mail})
    return User(response["data"]["id"], response["data"]["telegramID"], response["data"]["mail"]) \
        if response["code"] == 200 else None


def getOrCreate_user(telegramID):
    user = get_user(telegramID)
    if not user:
        user = add_user(telegramID)
    return get_user(telegramID)


def update_payment(userID, payment):
    pass
    # if get_user(userID):
    #     return request("POST", "/client.create", {"telegramID": userID})


def update_email(telegramID, mail):
    user = get_user(telegramID)
    if user:
        return request("POST", "/client.update", {"id": user.id, "mail": mail})
