import json

from utils.db_api import db
import time


def create_order_provisional(userID, text, document, percent, discount):
    db.DataBase.request(
        """INSERT INTO `orders_processing`(`userID`, `text`, `document` ,`active`, `percent`, `discount`, `date`) VALUES ({userID},"{text}",'{document}',1,{percent},{discount},{date})""".format(
            userID=userID, text=text, document=json.dumps(document), percent=percent, discount=discount, date=int(time.time())))


def get_order_provisional(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `userID`, `text`, `document`, `active`, `percent`, `discount`, `date` FROM `orders_processing` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]),
                "text": response[2], "document": json.loads(response[3]), "active": bool(response[4]), "percent": bool(response[5]), "discount": response[6], "date": int(response[7])}
    except:
        return {"success": False}


def get_ALLOrders_provisional():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`,`userID`,`date` FROM `orders_processing` WHERE `active`=1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "date": int(var[2])})
        return {"success": out != [], "data": out}
    except:
        return {"success": False}


def updateActive_order(id):
    try:
        db.DataBase.request("""UPDATE `orders_processing` SET `active`=0 WHERE `id`={id}""".format(
            id=id))
        return {"success": True}
    except:
        return {"success": False}