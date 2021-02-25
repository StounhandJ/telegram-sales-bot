from utils.db_api.db import DataBase


def add_user(userID, email="", payment=0):
    return DataBase.request(
        "INSERT INTO `user_information`(`userID`, `email`, `payment`) VALUES (%(userID)s,%(email)s,%(payment)s)",
        {"userID": userID, "email": email, "payment": payment})


def update_payment(userID, payment):
    if add_user(userID, payment=payment)["code"] != 200:
        return DataBase.request("UPDATE `user_information` SET `payment`=`payment`+%(payment)s WHERE `userID`=%(userID)s",
                                {"userID": userID, "payment": payment})


def update_email(userID, email):
    if add_user(userID, email=email)["code"]!=200:
        return DataBase.request("UPDATE `user_information` SET `email`=%(email)s WHERE `userID`=%(userID)s",
                                {"userID": userID, "email": email})
