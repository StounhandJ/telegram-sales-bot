from utils.db_api import db
import time


def create_order(userID, productID, description):
    db.DataBase.request(
        """INSERT INTO `orders`( `userID`, `productID`, `description`, `date`) VALUES ({user},{productID},"{description}",{date})""".format(
            user=userID, productID=productID, description=description, date=int(time.time())))


def get_product(id):
    try:
        response = db.DataBase.request(
            """SELECT `name`,`description`,`price` FROM `products` WHERE `id`={id}""".format(
                id=id
            ))[0]
        return {"success": True, "name": response[0], "description": response[1], "price": response[2]}
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


def get_order(id):
    try:
        sql = """SELECT `id`,`userID`,`productID`,`description`,`date` FROM `orders` WHERE `id`={id}""".format(
                id=id)
        response = db.DataBase.request(sql)[0]
        return {"success": True, "id":int(response[0]),"userID": int(response[1]), "productID": int(response[2]), "description": response[3], "date": int(response[4])}
    except:
        return {"success": False}


def get_ALLOrders():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`,`userID`,`productID`,`date` FROM `orders` WHERE 1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "productID": int(var[2]), "date": int(var[3])})
        return {"success": True, "data": out}
    except:
        return {"success": False}
