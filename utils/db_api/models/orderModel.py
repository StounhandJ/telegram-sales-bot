import json

from utils.db_api.db import DataBase
import time


def create_order(userID, description, document, price):
    return DataBase.request(
        "INSERT INTO `orders`( `userID`, `description`,`document`,`price` ,`date`,`active`) VALUES (%(userID)s,%(description)s,%(document)s,%(price)s,%(date)s,1)",
        {"userID": userID, "description": description, "document": json.dumps(document), "price": price,
         "date": int(time.time())})


def get_order(id):
    return DataBase.request(
        "SELECT `id`,`userID`,`description`,`document`,`price`,`active`,`date` FROM `orders` WHERE `id`=%(id)s",
        {"id": id})


def get_ALLOrders():
    response = DataBase.request("SELECT `id`,`userID`,`date` FROM `orders` WHERE `active`=1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def updateActive_order(id):
    return DataBase.request("UPDATE `orders` SET `active`=0 WHERE `id`=%(id)s", {"id": id})
