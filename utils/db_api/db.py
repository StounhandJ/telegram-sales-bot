import pymysql.cursors
from data import config


class DataBase(object):

    @staticmethod
    def request(sql):
        try:
            con = pymysql.connect(config.IP, config.dbUSER,
                                  config.dbPASSWORD, config.DATABASE)
            cursor = con.cursor()
        except Exception as e:
            print('Error connect DataBase')
            return
        try:
            cursor.execute(sql)
        except Exception as e:
            pass
        con.commit()
        otv = cursor.fetchall()
        cursor.close()
        return otv