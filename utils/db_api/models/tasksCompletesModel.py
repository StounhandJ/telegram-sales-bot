import json

from utils.db_api.db import DataBase
import time


def create_task_complete(userID, orderID, departmentTAG, message, document):
    return DataBase.request(
        "INSERT INTO `tasks_completes`(`userID`, `orderID`, `departmentTag`, `message`, `document`, `date`) VALUES (%(userID)s,%(orderID)s,%(departmentTAG)s,%(message)s,%(document)s,%(date)s)",
        {"userID": userID, "orderID": orderID, "departmentTAG": departmentTAG, "message": message,
         "document": json.dumps(document),
         "date": int(time.time())})


def get_task_complete(id):
    return DataBase.request(
        "SELECT `id`, `userID`, `orderID`, `departmentTag`, `message`, `document`, `date` FROM `tasks_completes` WHERE `id`=%(id)s",
        {"id": id})


def get_all_tasks_completes():
    response = DataBase.request(
        "SELECT `id`, `userID`, `orderID`, `departmentTag`, `message`, `document`, `date` FROM `tasks_completes`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_time_tasks_completes(startTime, endTime):
    response = DataBase.request(
        "SELECT `id`, `userID`, `orderID`, `departmentTag`, `message`, `document`, `date` FROM `tasks_completes` WHERE `date`>%(startTime)s AND `date`<%(endTime)s",
        {"startTime": startTime, "endTime": endTime})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_user_tasks_completes(userID):
    response = DataBase.request(
        "SELECT `id`, `userID`, `orderID`, `departmentTag`, `message`, `document`, `date` FROM `tasks_completes` WHERE `userID`=%(userID)s",
        {"userID": userID})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_orderID_tasks_completes(orderID):
    response = DataBase.request(
        "SELECT `id`, `userID`, `orderID`, `departmentTag`, `message`, `document`, `date` FROM `tasks_completes` WHERE `orderID`=%(orderID)s",
        {"orderID": orderID})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def del_tasks_completes(id):
    return DataBase.request(
        "DELETE FROM `tasks_completes` WHERE `id`=%(id)s",
        {"id": id})


def del_task_duplicate(userID, departmentTag, orderID):
    return DataBase.request(
        "DELETE FROM `tasks_completes` WHERE `userID`=%(userID)s AND `orderID`=%(orderID)s AND `departmentTag`=%(departmentTag)s",
        {"userID": userID, "orderID": orderID, "departmentTag": departmentTag})
