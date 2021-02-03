from utils.db_api import db
import time


def create_payment(userID, nameProduct, description, price, secret_key):
    try:
        db.DataBase.request(
            """INSERT INTO `payment`(`userID`, `nameProduct`, `description`, `price`, `secret_key`,`date`) VALUES ({userID},"{nameProduct}","{description}",{price},"{secret_key}",{date})""".format(
                userID=userID, nameProduct=nameProduct, description=description, price=price, secret_key=secret_key,
                date=int(time.time())))
        return {"success": True}
    except:
        return {"success": False}


def get_payment(userID):
    try:
        response = db.DataBase.request(
            """SELECT `nameProduct`, `description`, `price`, `secret_key`, `date` FROM `payment` WHERE `userID`={id}""".format(
                id=userID))[0]
        return {"success": True, "nameProduct": response[0], "description": response[1], "price": int(response[2]),
                "secret_key": response[3], "date": int(response[4])}
    except:
        return {"success": False}


def del_payment(userID):
    try:
        db.DataBase.request(
            """DELETE FROM `payment` WHERE `userID`={id}""".format(
                id=userID))
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
