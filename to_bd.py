import pandas as pd
import psycopg2
from database import *
from models import *
import random


#conn = psycopg2.connect(database='metro', user='aleksandralekseev', host='localhost', password='')
conn = psycopg2.connect(database='metro', user='postgres', host='localhost', password='1712')


def to_bd_passengers():
    df = pd.read_json('data/Заявки.json')
    df.drop_duplicates(subset='id_pas', keep="last", inplace=True)
    # Список id_pas
    id_pas_list = df.id_pas.tolist()

    # Функция для генерации случайного ФИО
    def generate_random_fio():
        last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнова", "Попова"]
        first_names = ["Иван", "Петр", "Александр", "Елена", "Ольга", "Михаил"]
        middle_names = ["Иванович", "Петрович", "Александрович", "Евгеньевна", "Олеговна", "Михайлович"]
        return f"{random.choice(last_names)} {random.choice(first_names)} {random.choice(middle_names)}"

    # Функция для генерации случайного телефона
    def generate_random_phone():
        return f"+7(9{random.randint(10, 99)}){random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"

    # Функция для генерации случайного телеграм ника
    def generate_random_telegram():
        adjectives = ["happy", "sad", "lucky", "unlucky", "brave", "shy"]
        animals = ["dog", "cat", "rabbit", "turtle", "penguin", "hamster"]
        numbers = [str(i) for i in range(10)]
        return f"@{random.choice(adjectives)}_{random.choice(animals)}{random.choice(numbers)}"

    # Создание DataFrame
    passengers_data = {
        "id_pas": id_pas_list,
        "fio": [generate_random_fio() for _ in range(210)],
        "cat_pas": df.cat_pas.tolist(),
        "phone": [generate_random_phone() for _ in range(210)],
        "telegram": [generate_random_telegram() for _ in range(210)]
    }

    passengers_df = pd.DataFrame(passengers_data)
    cur = conn.cursor()
    cur.execute("delete from passengers;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in passengers_df.iterrows():
        db = SessionLocal()
        new_passenger = {
            "id_pas": row['id_pas'],
            "fio": row['fio'],
            "cat_pas": row['cat_pas'],
            "phone": row['phone'],
            "telegram": row['telegram']
        }

        # Создаем объект Passengers с данными
        passenger_to_add = Passengers(**new_passenger)
        db.add(passenger_to_add)
        db.commit()
        db.close()


def to_bd_request():
    df = pd.read_json('data/Заявки.json')
    df.rename(columns={'id': 'ID_BID'}, inplace=True)
    df_ot = pd.read_json('data/Отмены заявок.json')
    df_ot.rename(columns={'DATE_TIME': 'otmena_datetime'}, inplace=True)
    df = df.merge(df_ot, how='left', on='ID_BID')
    df_per = pd.read_json('data/Переносы заявок по времени.json')
    df_per.rename(columns={'time_edit': 'time_perenos', 'id_bid': 'ID_BID'}, inplace=True)
    df = df.merge(df_per, how='left', on='ID_BID')
    df_n = pd.read_json('data/Неявка пассажира.json')
    df_n.rename(columns={'DATE_TIME': 'neyavka_datetime'}, inplace=True)
    df = df.merge(df_n, how='left', on='ID_BID')
    df.otmena_datetime = df.otmena_datetime.astype(object).where(df.otmena_datetime.notnull(), None)
    df.neyavka_datetime = df.neyavka_datetime.astype(object).where(df.neyavka_datetime.notnull(), None)
    cur = conn.cursor()
    cur.execute("delete from request;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()
        new_request = {
            "id_bid": row['ID_BID'],
            "id_pas": row['id_pas'],
            "datetime": row['datetime'],
            "time3": row['time3'],
            "time4": row['time4'],
            "cat_pas": row['cat_pas'],
            "status": row['status'],
            "tpz": row['tpz'],
            "insp_sex_m": row['INSP_SEX_M'],
            "insp_sex_f": row['INSP_SEX_F'],
            "time_over": row['TIME_OVER'],
            "id_st1": row['id_st1'],
            "id_st2": row['id_st2'],
            "otmena_datetime": row['otmena_datetime'],
            "neyavka_datetime": row['neyavka_datetime'],
            "time_perenos": row['time_perenos'],
            "phone": "",
            "telegram": "",
            "feedback": ""
        }
        # Создаем объект Request с данными
        request_to_add = Request(**new_request)
        db.add(request_to_add)
        db.commit()
        db.close()


def to_bd_time_perehod():
    df = pd.read_json('data/Метро время пересадки между станциями.json')
    df.time = df.time.astype('object')
    df.id1 = df.id1.astype('object')
    df.id2 = df.id2.astype('object')
    df.drop_duplicates(inplace=True)
    cur = conn.cursor()
    cur.execute("delete from time_perehod;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()
        new_time_perehod = {
            "id_st1": row['id1'],
            "id_st2": row['id2'],
            "time_perehod": row['time']
        }
        # Создаем объект TimePerehod с данными
        time_perehod_to_add = TimePerehod(**new_time_perehod)
        db.add(time_perehod_to_add)
        db.commit()
        db.close()


def to_bd_time_stations():
    df = pd.read_json('data/Метро время между станциями.json')
    df.drop_duplicates(inplace=True)
    cur = conn.cursor()
    cur.execute("delete from time_stations;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()
        new_time_station = {
            "id_st1": row['id_st1'],
            "id_st2": row['id_st2'],
            "time_way": row['time']
        }

        # Создаем объект TimeStations с данными
        time_station_to_add = TimeStations(**new_time_station)
        db.add(time_station_to_add)
        db.commit()
        db.close()


def to_bd_workers():
    df = pd.read_json('data/Сотрудники.json')
    cur = conn.cursor()
    cur.execute("delete from workers;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()
        new_worker_data = {
            "id_worker": row['ID'],
            "date": row['DATE'],
            "time_work": row['TIME_WORK'],
            "uchastok": row['UCHASTOK'],
            "smena": row['SMENA']
        }
        # Создаем объект Workers с данными
        worker_to_add = Workers(**new_worker_data)
        db.add(worker_to_add)
        db.commit()
        db.close()


def to_bd_workers_info():
    df = pd.read_json('data/Сотрудники.json')
    df.drop_duplicates(subset='ID', keep="last", inplace=True)
    cur = conn.cursor()
    cur.execute("delete from workers_info;")
    conn.commit()
    cur.close()
    #conn.close()
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()
        new_worker = {
            "id_worker": row['ID'],
            "fio": row['FIO'],
            "rank": row['RANK'],
            "sex": row['SEX'],
            "mobile_phone": "+79991234567",
            "phone_job": "+74951234567",
            "tabel_number": "12345",
            "health": ""
        }
        worker_to_add = WorkersInfo(**new_worker)
        db.add(worker_to_add)
        db.commit()
        db.close()

def to_bd_name_stations():
    df = pd.read_csv('stations.csv')
    df1 = pd.read_csv('cord.csv', sep=';')
    df = pd.merge(df, df1, on='name_station', how='left')
    cur = conn.cursor()

    cur.execute("delete from name_stations;")

    conn.commit()
    cur.close()

    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()

        data = {
            "id_station": row['id'],
            "name_station": row["name_station"],
            "name_line": "",
            "id_line": row["id_line"],
            "coordinate1": row["cord1"],
            "coordinate2": row["cord2"]

        }
        station_to_add = NameStations(**data)
        db.add(station_to_add)
        db.commit()
        db.close()


def to_bd_move():
    df = pd.read_csv('ts.csv')
    cur = conn.cursor()

    cur.execute("delete from move;")

    conn.commit()
    cur.close()

    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        #print(row['id'])
        db = SessionLocal()

        new_move = Move(
            id_bid=row["request_id"],
            id_worker=row["worker_id"],
            st_from=row["st1"],
            start_time=row["start_request_time"],
            on_place_time=row["on_place_time"],
            wait_minutes=row["wait_minutes"],
            time3=row["start_time"],
            name_station1=row["st1"],
            name_station2=row["st2"],
            path_minutes=row["path_minutes"],
            time4=row["end_time"],
            minutes_to_st1=row["minutes_to_st1"]
        )


        db.add(new_move)
        db.commit()
        db.close()

    # df = pd.read_csv('obed.csv')
    # cur = conn.cursor()
    #
    # cur.execute("delete from obed;")
    #
    # conn.commit()
    # cur.close()
    #
    # # Вставляем данные из датафрейма в таблицу базы данных
    # for index, row in df.iterrows():
    #     # print(row['id'])
    #     db = SessionLocal()
    #
    #     new_move = Obed(
    #         id_bid=row["request_id"],
    #         id_worker=row["worker_id"],
    #         st_from=row["st1"],
    #         start_time=row["start_request_time"],
    #         on_place_time=row["on_place_time"],
    #         wait_minutes=row["wait_minutes"],
    #         time3=row["start_time"],
    #         name_station1=row["st1"],
    #         name_station2=row["st2"],
    #         path_minutes=row["path_minutes"],
    #         time4=row["end_time"],
    #         minutes_to_st1=row["minutes_to_st1"]
    #     )
    #
    #     db.add(new_move)
    #     db.commit()
    #     db.close()

def to_bd_obed():
    df = pd.read_csv('obed.csv')
    cur = conn.cursor()

    cur.execute("delete from obed1;")

    conn.commit()
    cur.close()

    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():
        db = SessionLocal()

        new_move = Obed(
            id_worker=row["worker_id"],
            start_time=row["start_time"],
            end_time=row["end_time"]
        )

        db.add(new_move)
        db.commit()
        db.close()

    conn.close()


# if __name__ == '__main__':
#     to_bd_obed()
    #to_bd_move()
    #to_bd_request()
    # to_bd_workers()
    # to_bd_name_stations()
    # to_bd_passengers()
    # to_bd_time_perehod()
    # to_bd_workers_info()
    # to_bd_time_stations()


