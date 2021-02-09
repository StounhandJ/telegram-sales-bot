import json

from utils.db_api import db
import time


def create_messages(userID, message, document, isOrder):
    try:
        db.DataBase.request(
            """INSERT INTO `messages`(`userID`, `message`, `document`, `isOrder`, `active`, `date`) VALUES ({userID},"{message}",'{document}',{isOrder},1,{date})""".format(
                userID=userID, message=message, document=json.dumps(document), isOrder=isOrder, date=int(time.time())))
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
            """SELECT `id`, `userID`, `message`, `document`, `isOrder`, `active`, `date` FROM `messages` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "userID": int(response[1]),
                "message": response[2], "document": json.loads(response[3]), "isOrder": bool(response[4]),
                "active": bool(response[5]), "date": int(response[6])}
    except:
        return {"success": False}


def updateActive_message(id):
    try:
        db.DataBase.request("""UPDATE `messages` SET `active`=0 WHERE `id`={id}""".format(
            id=id))
        return {"success": True}
    except:
        return {"success": False}
