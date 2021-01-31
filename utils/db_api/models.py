from utils.db_api import db
import time


def create_order(userID, productID, description):
    db.DataBase.request(
        """INSERT INTO `orders`( `userID`, `productID`, `description`, `date`) VALUES ({user},{productID},"{description}",{date})""".format(
            user=userID, productID=productID, description=description, date=int(time.time())))


def get_product(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`,`name`,`description`,`price` FROM `products` WHERE `id`={id}""".format(
                id=id
            ))[0]
        return {"success": True, "id": int(response[0]), "name": response[1], "description": response[2],
                "price": int(response[3])}
    except:
        return {"success": False}


def get_ALLProducts():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`,`name`,`description`,`price` FROM `products` WHERE 1""".format(
                id=id)):
            out.append({"id": int(var[0]), "name": var[1], "description": var[2], "price": int(var[3])})
        return {"success": True, "data": out}
    except:
        return {"success": False}


def create_product(name, description, price):
    try:
        sql = """INSERT INTO `products`( `name`, `description`, `price`) VALUES ("{name}","{description}",{price})""".format(
            name=name, description=description, price=price
        )
        db.DataBase.request(sql)
        return {"success": True}
    except:
        return {"success": False}


def update_product(id, name, description, price):
    try:
        sql = """UPDATE `products` SET `name`="{name}",`description`="{description}",`price`={price} WHERE `id`={id}""".format(
            id=id, name=name, description=description, price=price
        )
        db.DataBase.request(sql)
        return {"success": True}
    except:
        return {"success": False}


def get_order(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`,`userID`,`productID`,`description`,`active`,`date` FROM `orders` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]), "productID": int(response[2]),
                "description": response[3], "active": bool(response[4]), "date": int(response[5])}
    except:
        return {"success": False}


def get_ALLOrders():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`,`userID`,`productID`,`date` FROM `orders` WHERE `active`=1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "productID": int(var[2]), "date": int(var[3])})
        return {"success": True, "data": out}
    except:
        return {"success": False}


def updateActive_order(id):
    try:
        db.DataBase.request("""UPDATE `orders` SET `active`=0 WHERE `id`={id}""".format(
            id=id))
        return {"success": True}
    except:
        return {"success": False}
