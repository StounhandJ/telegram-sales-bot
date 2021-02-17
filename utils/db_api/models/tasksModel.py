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
    userID = str(userID)
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `message` FROM `tasks` WHERE `staff` LIKE %(userOne)s OR `staff` LIKE %(userTwo)s",
        {"userOne": "%" + userID + ",%", "userTwo": "%" + userID + "]%"})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def del_task(id):
    return DataBase.request(
        "DELETE FROM `tasks` WHERE `id`=%(id)s",
        {"id": id})


def del_task_orderID(orderID):
    return DataBase.request(
        "DELETE FROM `tasks` WHERE `orderID`=%(orderID)s",
        {"orderID": orderID})


def del_task_duplicate(userID, orderID):
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `message` FROM `tasks` WHERE `staff` LIKE %(userOne)s OR `staff` LIKE %(userTwo)s",
        {"userOne": "%" + str(userID) + ",%", "userTwo": "%" + str(userID) + "]%"})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    if response["code"] == 200:
        for task in response["data"]:
            if task["orderID"] == orderID:
                if len(task["staff"]) == 1:
                    DataBase.request(
                        "DELETE FROM `tasks` WHERE `id`=%(id)s",
                        {"id": task["id"]})
                else:
                    DataBase.request(
                        "UPDATE `tasks` SET `staff`=%(staff)s WHERE `id`=%(id)s",
                        {"staff": json.dumps(task["staff"].remove(userID)), "id": task["id"]})
