import json
import pandas as pd
import networkx as nx
from datetime import timedelta, datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


def algos():
    conn = 'postgresql://postgres:1712@localhost/metro'
    #conn = 'postgresql://aleksandralekseev:@localhost/metro'
    #conn = 'postgresql://postgres:1712@alexbobr.ru/metro'

    with_client_delay = 5 * 60
    alone_delay = 3 * 60

    # station_names = pd.read_json('Наименование станций метро.json').set_index('id')['name_station'].drop_duplicates()
    station_names = pd.read_sql_table(table_name='name_stations', con=conn) \
        .set_index('id_station')['name_station'].drop_duplicates()


    def min2sec(t):
        if isinstance(t, int):
            return t * 60
        t = tuple(map(int, t.split(',')))
        if len(t) == 1:
            return t[0] * 60
        else:
            return t[0] * 60 + t[1] * 10


    # ride_time = pd.read_json('Метро время между станциями.json')
    ride_time = pd.read_sql_table(table_name='time_stations', con=conn)
    ride_time.columns = ['id_st1', 'id_st2', 'time']
    ride_time.time = ride_time.time.map(min2sec)
    ride_time['go'] = False

    # go_time = pd.read_json('Метро время пересадки между станциями.json')
    go_time = pd.read_sql_table(table_name='time_perehod', con=conn)
    go_time.columns = ['id_st1', 'id_st2', 'time']
    go_time.time = go_time.time.map(min2sec)
    go_time['go'] = True

    go_time_alone = go_time.copy()
    go_time_alone.time += alone_delay

    go_time_client = go_time.copy()
    go_time_client.time += with_client_delay

    time_alone = pd.concat([ride_time, go_time_alone])
    time_client = pd.concat([ride_time, go_time_client])
    for col in 'id_st1', 'id_st2':
        for df in time_alone, time_client:
            df[col] = df[col].map(station_names)

    metro_alone = nx.from_pandas_edgelist(df=time_alone,
                                          source='id_st1',
                                          target='id_st2',
                                          edge_attr=True)

    metro_client = nx.from_pandas_edgelist(df=time_client,
                                           source='id_st1',
                                           target='id_st2',
                                           edge_attr=True)


    def get_path(st1, st2, alone=True):
        if st1 in ('Старт', 'Обед', st2):
            return {'time': 0, 'path': []}

        graph = metro_alone if alone else metro_client
        time = nx.shortest_path_length(graph, source=st1, target=st2, weight='time')
        path = nx.shortest_path(graph, source=st1, target=st2, weight='time')
        for i in range(len(path) - 1):
            if graph[path[i]][path[i + 1]]['go']:
                path[i] = path[i], 'go', graph[path[i]][path[i + 1]]['time']
            else:
                path[i] = path[i], 'ride', graph[path[i]][path[i + 1]]['time']
        path[-1] = path[-1], 'final', 0
        return {'time': time + (alone_delay if alone else with_client_delay), 'path': path}

    #workers = pd.read_json('Сотрудники.json').set_index('ID')
    workers = pd.merge(pd.read_sql_table(table_name='workers', con=conn),
                       pd.read_sql_table(table_name='workers_info', con=conn))
    workers = workers.set_index('id_worker')[['fio', 'rank', 'sex', 'time_work']]
    workers.index = workers.index.astype(int)
    workers.sex = workers.sex.apply(lambda x: x[0].lower())
    workers['start_hour'] = workers.time_work.apply(lambda x: int(x.split(':')[0]))
    workers['end_hour'] = workers.time_work.apply(lambda x: int(x.split('-')[1].split(':')[0]))
    workers = workers.loc[workers['rank'].isin(['ЦИ', 'ЦСИ'])]
    day_workers = workers[workers.start_hour < workers.end_hour]
    # Разобъём ночных работиников на 2 категории: утро и вечер (нужно для адекватной работы алгоритма)
    night_workers = workers[workers.end_hour < workers.start_hour]
    morning_workers = night_workers.copy()
    morning_workers['start_hour'] = 0
    evening_workers = night_workers.copy()
    evening_workers['end_hour'] = 25
    evening_workers.index += 100_000

    workers = pd.concat([day_workers, morning_workers, evening_workers]).drop_duplicates().drop(columns='time_work')

    def get_requests():
        # requests = pd.read_json('Заявки.json').set_index('id')
        requests = pd.read_sql_table(table_name='request', con=conn,
                                     columns=['id_pas',
                                              'datetime',
                                              'insp_sex_m',
                                              'insp_sex_f',
                                              'id_st1',
                                              'id_st2',
                                              'otmena_datetime',
                                              'neyavka_datetime',
                                              'time_perenos'],
                                     index_col='id_bid')

        for col in 'id_st1', 'id_st2':
            requests[col] = requests[col].map(station_names)

        for col in 'datetime', 'otmena_datetime', 'neyavka_datetime', 'time_perenos':
            requests[col] = pd.to_datetime(requests[col], format='mixed')

        # Удаляем все отменённые заявки
        requests = requests[requests.otmena_datetime.isnull()]

        # Делаем все переносы
        make_shift = lambda x: x['time_perenos'] if not pd.isnull(x['time_perenos']) else x['datetime']
        requests['datetime'] = requests.apply(make_shift,
                                              axis=1)

        # Меняем дату на сегодняшнюю
        today = datetime.now().date()
        requests['datetime'] = requests['datetime'].map(lambda x: datetime(year=today.year,
                                                                           month=today.month,
                                                                           day=today.day,
                                                                           hour=x.hour,
                                                                           minute=x.minute,
                                                                           second=x.second))

        calc_path_time = lambda x: timedelta(seconds=get_path(st1=x.id_st1, st2=x.id_st2, alone=False)['time'])
        requests['path_time'] = requests.apply(
            lambda x: calc_path_time(x) if pd.isnull(x['neyavka_datetime']) else timedelta(0),
            axis=1)

        calc_end_time = lambda x: x['datetime'] + x['path_time']
        requests['end_time'] = requests.apply(
            lambda x: calc_end_time(x) if pd.isnull(x['neyavka_datetime']) else x['neyavka_datetime'],
            axis=1)

        requests.drop(columns=['otmena_datetime', 'neyavka_datetime', 'time_perenos'], inplace=True)
        return requests.sort_values('datetime')

    requests = get_requests()
    today = requests.iloc[0]['datetime'].date()

    requests = get_requests()
    today = requests.iloc[0]['datetime'].date()


    requests = get_requests()
    today = requests.iloc[0]['datetime'].date()


    def hour2datetime(hour, date=today):
        return datetime(year=date.year,
                        month=date.month,
                        day=date.day,
                        hour=hour)


    def get_timesheet(requests):
        timesheet = pd.DataFrame(columns=['st_from',
                                          'start_time',
                                          'minutes_to_st1',
                                          'on_place_time',
                                          'wait_minutes',
                                          'start_request_time',
                                          'st1',
                                          'st2',
                                          'path_minutes',
                                          'end_time'],
                                 index=pd.MultiIndex.from_arrays([[-1] * len(workers), workers.index],
                                                                 names=('request_id', 'worker_id')))

        timesheet.st2 = 'Старт'
        timesheet.end_time = workers['start_hour'].apply(hour2datetime).values
        timesheet.sort_values('end_time', inplace=True)

        def get_on_place_time(row, st2):
            last_request = timesheet.xs(row.name, level='worker_id').iloc[-1]
            time_to_st1 = get_path(st1=last_request['st2'], st2=st2)['time']
            return last_request['end_time'] + timedelta(seconds=time_to_st1)

        for request_id, request in tqdm(requests.iterrows(), desc='Обработка заявок', total=len(requests)):
            # Отфильтровываем тех, кто не успеет выполнить заявку до конца рабочего дня
            possible_workers = workers[request['end_time'].hour <= workers.end_hour]
            # Смотрим сколько нужно женщин и мужчин
            possible_idxs = []
            for sex, count in zip(('м', 'ж'), request[['insp_sex_m', 'insp_sex_f']]):
                count = int(count)
                if count == 0:
                    continue
                spw = possible_workers[possible_workers.sex == sex]
                spw['on_place_time'] = spw.apply(lambda x: get_on_place_time(x, request['id_st1']),
                                                 axis=1)
                possible_idxs.extend(spw.sort_values('on_place_time').index[:count])

            for worker_id in possible_idxs:
                last_request = timesheet.xs(worker_id, level='worker_id').iloc[-1]
                time_to_st1 = get_path(st1=last_request['st2'], st2=request['id_st1'])['time']
                on_place_time = last_request['end_time'] + timedelta(seconds=time_to_st1)
                if last_request['st2'] == 'Старт':
                    wait_minutes = 15
                else:
                    wait_minutes = int((request['datetime'] - on_place_time).total_seconds()) // 60

                if wait_minutes >= 60:
                    timesheet.loc[(-1, worker_id), :] = {'st_from': request['id_st1'],
                                                         'start_time': on_place_time,
                                                         'minutes_to_st1': 0,
                                                         'on_place_time': on_place_time,
                                                         'wait_minutes': 0,
                                                         'start_request_time': request['datetime'] - timedelta(hours=1),
                                                         'st1': 'Обед',
                                                         'st2': request['id_st2'],
                                                         'path_minutes': 60,
                                                         'end_time': request['datetime']}

                timesheet.loc[(request_id, worker_id % 100_000), :] = {'st_from': last_request['st2'],
                                                                       'start_time': last_request['end_time'],
                                                                       'minutes_to_st1': time_to_st1 // 60,
                                                                       'on_place_time': on_place_time,
                                                                       'wait_minutes': wait_minutes,
                                                                       'start_request_time': request['datetime'],
                                                                       'st1': request['id_st1'],
                                                                       'st2': request['id_st2'],
                                                                       'path_minutes': int(
                                                                           request['path_time'].total_seconds()) // 60,
                                                                       'end_time': request['end_time']}

        return timesheet.dropna()

    #move
    ts = get_timesheet(requests)
    obed = ts.xs(-1, level=0)[['start_request_time', 'end_time']]
    obed.columns = ['start_time', 'end_time']
    ts = ts[ts.index.get_level_values(0) != -1]
    obed.to_csv('obed.csv')
    ts.to_csv('ts.csv')








