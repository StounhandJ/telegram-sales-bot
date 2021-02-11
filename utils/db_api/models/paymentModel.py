import json

from utils.db_api.db import DataBase
import time


def create_payment(userID, description, document, price, secret_key):
    return DataBase.request(
        "INSERT INTO `payment`(`userID`, `description`, `document`, `price`, `secret_key`,`date`) VALUES (%(userID)s,%(description)s,%(document)s,%(price)s,%(secret_key)s,%(date)s)",
        {"userID": userID, "description": description, "document": json.dumps(document), "price": price,
         "secret_key": secret_key,
         "date": int(time.time())})


def get_payment(secret_key):
    return DataBase.request(
        "SELECT `userID`, `description`, `document`, `price`, `secret_key`, `date` FROM `payment` WHERE `secret_key`=%(secret_key)s",
        {"secret_key": secret_key})


def del_payment(secret_key):
    return DataBase.request("DELETE FROM `payment` WHERE `secret_key`=%(secret_key)s", {"secret_key": secret_key})


def add_payment_history(userID, amount):
    return DataBase.request(
        "INSERT INTO `payment_history`(`userID`, `amount`, `date`) VALUES (%(userID)s,%(amount)s,%(date)s)",
        {"userID": userID, "amount": amount, "date": int(time.time())})
