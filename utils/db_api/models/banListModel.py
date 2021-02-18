import time

from utils.db_api.db import DataBase


def add_ban(userID):
    return DataBase.request("INSERT INTO `ban_list`(`userID`, `date`) VALUES (%(userID)s,%(date)s)",
                            {"userID": userID, "date": time.time()})


def del_ban(userID):
    return DataBase.request("DELETE FROM `ban_list` WHERE `userID`= %(userID)s",
                            {"userID": userID})


def get_ban_user(userID):
    return DataBase.request("SELECT `id`, `userID`, `date` FROM `ban_list` WHERE `userID`=%(userID)s",
                            {"userID": userID})


def get_all_ban():
    response = DataBase.request("SELECT `id`, `userID`, `date` FROM `ban_list` WHERE 1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response
