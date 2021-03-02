import json

from utils.db_api.db import DataBase


class Task:

    def __init__(self, id, orderID, staff, departmentTag, message):
        self.id = id
        self.orderID = orderID
        self.staff = staff
        self.departmentTag = departmentTag
        self.message = message


def create_task(orderID, staff, tag, message):
    return DataBase.request(
        "INSERT INTO `tasks`(`orderID`, `staff`, `departmentTag`,`message`) VALUES (%(orderID)s,%(staff)s,%(tag)s,%(message)s)",
        {"orderID": orderID, "staff": json.dumps(staff), "tag": tag, "message": message})


def get_task(id):
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `departmentTag`, `message` FROM `tasks` WHERE `id`=%(id)s",
        {"id": id})
    task = None
    if response["code"] == 200:
        task = Task(response["data"]["id"], response["data"]["orderID"], response["data"]["staff"],
                    response["data"]["departmentTag"],
                    response["data"]["message"])
    return task


def get_tasks(page=0, max_size=10):
    response = DataBase.request(
        "SELECT t1.id, t1.orderID, t1.staff, t1.departmentTag, t1.message FROM `tasks` t1 INNER JOIN (SELECT DISTINCT `orderID` FROM tasks LIMIT %(page)s,%(max_size)s) t2 ON t2.orderID=t1.orderID",
        {"page": page * max_size, "max_size": max_size})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    tasks = []
    for task in response["data"]:
        tasks.append(Task(task["id"], task["orderID"], task["staff"], task["departmentTag"], task["message"]))
    return tasks


def get_tasks_count():
    response = DataBase.request("SELECT COUNT(DISTINCT `orderID`) AS 'count' FROM `tasks`")
    return response["data"]["count"] if response["code"] == 200 else 0


def get_user_tasks(userID):
    userID = str(userID)
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `departmentTag`, `message` FROM `tasks` WHERE `staff` LIKE %(userOne)s OR `staff` LIKE %(userTwo)s",
        {"userOne": "%" + userID + ",%", "userTwo": "%" + userID + "]%"})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    tasks = []
    for task in response["data"]:
        tasks.append(Task(task["id"], task["orderID"], task["staff"], task["departmentTag"], task["message"]))
    return tasks


def del_task(id):
    return DataBase.request(
        "DELETE FROM `tasks` WHERE `id`=%(id)s",
        {"id": id})


def del_task_orderID(orderID):
    return DataBase.request(
        "DELETE FROM `tasks` WHERE `orderID`=%(orderID)s",
        {"orderID": orderID})


def del_task_duplicate(userID, departmentTag, orderID):
    response = DataBase.request(
        "SELECT `id`, `orderID`, `staff`, `departmentTag`, `message` FROM `tasks` WHERE `departmentTag`=%(departmentTag)s AND (`staff` LIKE %(userOne)s OR `staff` LIKE %(userTwo)s)",
        {"departmentTag": departmentTag, "userOne": "%" + str(userID) + ",%", "userTwo": "%" + str(userID) + "]%"})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    if response["code"] == 200:
        for task in response["data"]:
            if task["orderID"] == orderID:
                if len(task["staff"]) == 1:
                    DataBase.request(
                        "DELETE FROM `tasks` WHERE `id`=%(id)s",
                        {"id": task["id"]})
                else:
                    task["staff"].remove(userID)
                    DataBase.request(
                        "UPDATE `tasks` SET `staff`=%(staff)s WHERE `id`=%(id)s",
                        {"staff": json.dumps(task["staff"]), "id": task["id"]})
