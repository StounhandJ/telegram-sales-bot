import json

from utils.db_api import db
import time


def create_order(userID, description, document, price):
    db.DataBase.request(
        """INSERT INTO `orders`( `userID`, `description`,`document`,`price` ,`date`,`active`) VALUES ({user},"{description}",'{document}',{price},{date},1)""".format(
            user=userID, description=description, document=json.dumps(document), price=price,
            date=int(time.time())))


def get_order(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`,`userID`,`description`,`document`,`price`,`active`,`date` FROM `orders` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]),
                "description": response[2], "document": json.loads(response[3]), "price": int(response[4]),
                "active": bool(response[5]), "date": int(response[6])}
    except:
        return {"success": False}


def get_ALLOrders():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`,`userID`,`date` FROM `orders` WHERE `active`=1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "date": int(var[2])})
        return {"success": out != [], "data": out}
    except:
        return {"success": False}


def updateActive_order(id):
    try:
        db.DataBase.request("""UPDATE `orders` SET `active`=0 WHERE `id`={id}""".format(
            id=id))
        return {"success": True}
    except:
        return {"success": False}
