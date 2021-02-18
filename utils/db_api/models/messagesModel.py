import json

from utils.db_api.db import DataBase
import time


def create_messages(userID, message, document, isOrder):
    return DataBase.request(
        "INSERT INTO `messages`(`userID`, `message`, `document`, `isOrder`, `active`, `date`) VALUES (%(userID)s,%(message)s,%(document)s,%(isOrder)s,1,%(date)s)",
        {"userID": userID, "message": message, "document": json.dumps(document), "isOrder": isOrder,
         "date": int(time.time())})


def get_all_messages():
    response = DataBase.request(
        "SELECT `id`,`userID`, `message`, `date` FROM `messages` WHERE `isOrder`= 0 AND`active`=1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_order_messages():
    response = DataBase.request(
        "SELECT `id`,`userID`, `message`, `date` FROM `messages` WHERE `isOrder`= 1 AND`active`=1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_message(id):
    return DataBase.request(
        "SELECT `id`, `userID`, `message`, `document`, `isOrder`, `active`, `date` FROM `messages` WHERE `id`=%(id)s",
        {"id": id})


def get_last_message_day_user(userID):
    response = DataBase.request(
        "SELECT `id`, `userID`, `message`, `document`, `isOrder`, `active`, `date` FROM `messages` WHERE `userID`=%(userID)s AND `date`>%(date)s",
        {"userID": userID, "date": time.time() - 60 * 60 * 24})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def updateActive_message(id):
    return DataBase.request("UPDATE `messages` SET `active`=0 WHERE `id`=%(id)s", {"id": id})
