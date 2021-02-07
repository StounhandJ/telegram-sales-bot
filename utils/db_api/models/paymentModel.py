import json

from utils.db_api import db
import time


def create_payment(userID, description, document, price, secret_key):
    try:
        db.DataBase.request(
            """INSERT INTO `payment`(`userID`, `description`, `document`, `price`, `secret_key`,`date`) VALUES ({userID},"{description}",'{document}',{price},"{secret_key}",{date})""".format(
                userID=userID, description=description, document=json.dumps(document), price=price, secret_key=secret_key,
                date=int(time.time())))
        return {"success": True}
    except:
        return {"success": False}


def get_payment(secret_key):
    try:
        response = db.DataBase.request(
            """SELECT `userID`, `description`, `document`, `price`, `secret_key`, `date` FROM `payment` WHERE `secret_key`="{secret_key}" """.format(
                secret_key=secret_key))[0]
        return {"success": True, "userID": response[0], "description": response[1], "document": json.loads(response[2]),
                "price": int(response[3]),
                "secret_key": response[4], "date": int(response[5])}
    except:
        return {"success": False}


def del_payment(secret_key):
    try:
        db.DataBase.request(
            """DELETE FROM `payment` WHERE `secret_key`="{secret_key}" """.format(
                secret_key=secret_key))
        return {"success": True}
    except:
        return {"success": False}


def add_payment_history(userID, amount):
    try:
        db.DataBase.request(
            """INSERT INTO `payment_history`(`userID`, `amount`, `date`) VALUES ({userID},{amount},{date})""".format(
                userID=userID, amount=amount, date=int(time.time())))
        return {"success": True}
    except:
        return {"success": False}
