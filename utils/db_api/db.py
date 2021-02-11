import json

import pymysql.cursors
from data import config


class DataBaseClass(object):

    def __init__(self):
        self.con = None
        self.cursor = None
        try:
            self.con = pymysql.connect(host=config.IP, user=config.dbUSER,
                                       password=config.dbPASSWORD, database=config.DATABASE,
                                       cursorclass=pymysql.cursors.DictCursor)
            self.cursor = self.con.cursor()
        except Exception as e:
            print('Error connect DataBase')

    def request(self, sql, data=None):
        if data is None:
            data = {}
        try:
            if self.con.ping(reconnect=True):
                return {"code": 502, "mes": "Reconnecting DataBase", "data": None}
        except:
            return {"code": 502, "mes": "Error connect DataBase", "data": None}

        try:
            self.cursor.execute(sql, data)
        except Exception as e:
            return {"code": 100, "mes": "Ошибка в запросе или указаны не все параметры", "data": None}

        self.con.commit()

        if self.cursor.rowcount == 0:
            return {"code": 404, "mes": "Совпдений не найдено", "data": None}
        try:
            out = []
            fetchall = self.cursor.fetchall()
            for key, value in enumerate(fetchall):
                out.append({})
                for key2, value2 in value.items():
                    try:
                        out[key][key2] = json.loads(value2)
                    except:
                        out[key][key2] = value2
            return {"code": 200, "mes": "Успешно", "data": out[0] if len(out) == 1 else out}
        except:
            return {"code": 204, "mes": "Успешно, но ответа нет", "data": None}


DataBase = DataBaseClass()
