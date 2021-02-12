import json

from utils.db_api.db import DataBase


def create_task(orderID, staff, message):
    return DataBase.request(
        "INSERT INTO `tasks`(`orderID`, `staff`, `message`) VALUES (%(orderID)s,%(staff)s,%(message)s)",
        {"orderID": orderID, "staff": json.dumps(staff), "message": message})


def get_task(id):
    return DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `message` FROM `tasks` WHERE `id`=%(id)s",
        {"id": id})


def get_all_tasks():
    response = DataBase.request("SELECT `id`, `orderID`, `staff`, `message` FROM `tasks`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_user_tasks(userID):
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `message` FROM `tasks` WHERE `staff` LIKE %(userOne)s OR `staff` LIKE %(userTwo)s",
        {"userOne": userID + ",", "userTwo": userID + "]"})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response

def del_task(id):
    return DataBase.request(
        "DELETE FROM `tasks` WHERE `id`=%(id)s",
        {"id": id})
