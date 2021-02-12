import json

from utils.db_api.db import DataBase
import time


def create_task_complete(taskID, userID, orderID, message, document):
    return DataBase.request(
        "INSERT INTO `tasks_completes`(`taskID`, `userID`, `orderID`, `message`, `document`, `date`) VALUES (%(taskID)s,%(userID)s,%(orderID)s,%(message)s,%(document)s,%(date)s)",
        {"taskID": taskID, "userID": userID, "orderID": orderID, "message": message, "document": json.loads(document),
         "date": int(time.time())})


def get_task_complete(id):
    return DataBase.request(
        "SELECT `id`, `taskID`, `userID`, `orderID`, `message`, `document`, `date` FROM `tasks_completes` WHERE `id`=%(id)s",
        {"id": id})


def get_all_tasks_completes():
    response = DataBase.request(
        "SELECT `id`, `taskID`, `userID`, `orderID`, `message`, `document`, `date` FROM `tasks_completes`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_user_tasks_completes(userID):
    response = DataBase.request(
        "SELECT `id`, `taskID`, `userID`, `orderID`, `message`, `document`, `date` FROM `tasks_completes` WHERE `userID`=%(userID)s",
        {"userID": userID})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_taskID_tasks_completes(taskID):
    response = DataBase.request(
        "SELECT `id`, `taskID`, `userID`, `orderID`, `message`, `document`, `date` FROM `tasks_completes` WHERE `taskID`=%(taskID)s",
        {"taskID": taskID})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_orderID_tasks_completes(orderID):
    response = DataBase.request(
        "SELECT `id`, `taskID`, `userID`, `orderID`, `message`, `document`, `date` FROM `tasks_completes` WHERE `orderID`=%(orderID)s",
        {"orderID": orderID})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def del_tasks_completes(id):
    return DataBase.request(
        "DELETE FROM `tasks_completes` WHERE `id`=%(id)s",
        {"id": id})
