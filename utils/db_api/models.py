from utils.db_api import db
import time


def create_order(userID, description, nameProduct, price):
    db.DataBase.request(
        """INSERT INTO `orders`( `userID`, `description`,`nameProduct`,`price` ,`date`,`active`) VALUES ({user},"{description}","{nameProduct}",{price},{date},1)""".format(
            user=userID, description=description, nameProduct=nameProduct, price=price,
            date=int(time.time())))


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
            """SELECT `id`,`userID`,`description`,`nameProduct`,`price`,`active`,`date` FROM `orders` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]),
                "description": response[2], "nameProduct": response[3], "price": int(response[4]),
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
                "secret_key": response[3],"date": int(response[4])}
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


def create_messages(userID, message, isOrder):
    try:
        db.DataBase.request(
            """INSERT INTO `messages`(`userID`, `message`, `isOrder`, `active`, `date`) VALUES ({userID},"{message}",{isOrder},1,{date})""".format(
                userID=userID, message=message, isOrder=isOrder, date=int(time.time())))
        return {"success": True}
    except:
        return {"success": False}


def get_all_messages():
    try:
        out = []
        for var in db.DataBase.request(
                """SELECT `id`,`userID`, `message`, `date` FROM `messages` WHERE `isOrder`= 0 AND`active`=1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "messages": var[2], "date": int(var[3])})
        return {"success": out != [], "data": out}
    except:
        return {"success": False}


def get_order_messages():
    try:
        out = []
        for var in db.DataBase.request(
                """SELECT `id`,`userID`, `message`, `date` FROM `messages` WHERE `isOrder`= 1 AND `active`=1"""):
            out.append({"id": int(var[0]), "userID": int(var[1]), "messages": var[2], "date": int(var[3])})
        return {"success": out != [], "data": out}
    except:
        return {"success": False}


def get_message(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `userID`, `message`, `isOrder`, `active`, `date` FROM `messages` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]),
                "message": response[2], "isOrder": bool(response[3]),
                "active": bool(response[4]), "date": int(response[5])}
    except:
        return {"success": False}


def updateActive_message(id):
    try:
        db.DataBase.request("""UPDATE `messages` SET `active`=0 WHERE `id`={id}""".format(
            id=id))
        return {"success": True}
    except:
        return {"success": False}
