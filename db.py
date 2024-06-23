import psycopg2
from settings import *
class Database():
    def __init__(self):
        self.con = psycopg2.connect(database=database,
                                    user=user,
                                    password=password,
                                    host=host,
                                    port=port
                                    )


    def get_all(self):
        cursor = self.con.cursor()
        cursor.execute(f"select  * from move join workers on move.id_worker = workers.id_worker join workers_info "
                       f"on workers_info.id_worker = workers.id_worker join request on  request.id_bid = move.id_bid;")
        result = cursor.fetchall()
        temp = []
        for x in result:
            temp2 = {}
            c = 0
            for col in cursor.description:
                temp2.update({str(col[0]): x[c]})
                c = c + 1
            temp.append(temp2)
        return temp

    def get_req(self, id_bid):
        cursor = self.con.cursor()
        cursor.execute(f"select r.*, m.id_worker, w.fio from request as r join move as m on r.id_bid = m.id_bid "
                       f"join workers_info as w on w.id_worker = m.id_worker where r.id_bid = '{id_bid}';")
        result = cursor.fetchall()
        temp = []
        for x in result:
            temp2 = {}
            c = 0
            for col in cursor.description:
                temp2.update({str(col[0]): x[c]})
                c = c + 1
            temp.append(temp2)
        return temp

    def get_work_stations(self, id_worker):
        cursor = self.con.cursor()
        cursor.execute(f"select m.name_station1 , m.name_station2, n.coordinate1 as p1c1, n.coordinate2 as p1c2,"
                       f" n1.coordinate1 as p2c1, n1.coordinate2 as p2c2  from move as m join name_stations as n on"
                       f" m.name_station1 = n.name_station join name_stations as n1"
                       f" on m.name_station2 = n1.name_station"
                       f" where id_worker = '{id_worker}';")
        result = cursor.fetchall()
        temp = []
        for x in result:
            temp2 = {}
            c = 0
            for col in cursor.description:
                temp2.update({str(col[0]): x[c]})
                c = c + 1
            temp.append(temp2)
        return temp