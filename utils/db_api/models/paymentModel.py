import json

from utils.db_api.db import DataBase
import time


class Payment:

    def __init__(self, id, userID, description, document, separate_payment, additional, price, secret_key, date):
        self.id = id
        self.userID = userID
        self.description = description
        self.document = document
        self.separate_payment = separate_payment
        self.additional = additional
        self.price = price
        self.secret_key = secret_key
        self.date = date

    def del_payment(self):
        return DataBase.request("DELETE FROM `payment` WHERE `secret_key`=%(secret_key)s", {"secret_key": self.secret_key})


def create_payment(userID, description, document, separate_payment, price, secret_key, additional):
    return DataBase.request(
        "INSERT INTO `payment`(`userID`, `description`, `document`, `separate_payment`,`additional`,`price`, `secret_key`,`date`) VALUES (%(userID)s,%(description)s,%(document)s,%(separate_payment)s,%(additional)s,%(price)s,%(secret_key)s,%(date)s)",
        {"userID": userID, "description": description, "document": json.dumps(document),
         "separate_payment": separate_payment, "price": price,
         "secret_key": secret_key, "additional":additional,
         "date": int(time.time())})


def get_payment(secret_key):
    response = DataBase.request(
        "SELECT `id`, `userID`, `description`, `document`, `separate_payment`,`additional`, `price`, `secret_key`, `date` FROM `payment` WHERE `secret_key`=%(secret_key)s",
        {"secret_key": secret_key})
    payment = None
    if response["code"] == 200:
        payment = Payment(response["data"]["id"], response["data"]["userID"], response["data"]["description"], response["data"]["document"],
                                response["data"]["separate_payment"], response["data"]["additional"], response["data"]["price"], response["data"]["secret_key"], response["data"]["date"])
    return payment


def add_payment_history(userID, amount):
    return DataBase.request(
        "INSERT INTO `payment_history`(`userID`, `amount`, `date`) VALUES (%(userID)s,%(amount)s,%(date)s)",
        {"userID": userID, "amount": amount, "date": int(time.time())})
