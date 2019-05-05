import pandas as pd
import numpy as np
from pandas import Series
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib

import pyqtgraph as pg
import pyqtgraph.exporters



from copy import deepcopy


def parse_file(name, path):

    d = pd.read_csv(path + name, header=None)
    d = list(d.values.tolist())

    return d


def coin_type(name, path):
    coin = list(name)
    coin = list(coin)

    del coin[15:]
    del coin[:9]

    return ''.join(coin)


def fill_dates(data, currency, time_interval):
    _data = data.copy()
    for i in currency:
        _data[i] = parse_timestamps(_data[i], time_interval)
        pass
    return _data


def parse_timestamps(data, time_interval):

    _data = data.copy()
    _time = time_interval * 60 * 1000

    start = int(_data[0][0])
    end = int(_data[-1][0])
    length = int((end - start) / _time)

    count = 0

    for i in range(length - 1):
        if _data[i][0] != _data[i+1][0] - _time:
            _ = [_data[i][0] + _time, 0, 0, 0, 0, 0]
            _data.insert(i+1, _)
            count += 1
            pass

    for i in range(len(_data)):
        _data[i][0] = int(_data[i][0])
        if _data[i][2] == 0:
            first_price = _data[i-1][1]
            _c = 1
            while True:
                if _data[i+_c][2] != 0:
                    last_price = _data[i+_c][2]
                    break
                _c += 1
                if _c > 1000:
                    raise ValueError('infinite loop error while filling out timestamps with 0 price ')

            _data[i][2] = (first_price + last_price) / 2

            pass
        del _data[i][4]
        del _data[i][3]
        del _data[i][1]

        pass

    # print(count)


    return _data

def generate(file_list, path):

    d = dict()

    for i in file_list:

        coin = coin_type(i, path)

        _d = parse_file(i, path)

        d[coin] = _d

        pass

    return d


def save_file(data, name):

    df = pd.DataFrame(data)
    df.to_csv(name + '.csv', sep=',', index=False, header=False)

    pass


def build_price_movements(data, currency, time_interval):

    hour = int(60/time_interval)
    day = int(1440/time_interval)
    week = int(10080/time_interval)

    _data = data.copy()
    new_data = []

    for i in range(len(currency)):

        new_data.append(day_volume(_data[currency[i]], day)) # set the 24hr volume

        new_data[i] = time_change(new_data[i], hour)
        new_data[i] = time_change(new_data[i], day)
        new_data[i] = time_change(new_data[i], week)


        new_data[i] = day_volume_movement(new_data[i], week, day)

        del new_data[i][:week]
        pass

    # in case different currencies don't cover the full dataset, removed for the moment
    # start = new_data[0][0][0]
    #
    # for i in range(1, len(new_data)):
    #     while new_data[i][0][0] != start:
    #         new_data[i].insert(0, [new_data[i][0][0] - 900000, 0,0,0,0,0,0,0,0,0,0])

    return new_data

def build_price_movements_2(data, currency, time_interval):

    five_min = 1
    ten_min = 2
    fifteen_min = 3
    hour = int(60/time_interval)
    day = int(1440/time_interval)
    week = int(10080/time_interval)

    new_data = []

    for i in range(len(currency)):
        new_data.append([])

        for x in data[currency[i]]:
            new_data[i].append([x[0], x[1]])
            pass

        new_data[i] = time_change_2(data[currency[i]], new_data[i], [1, 2, 3, 4, hour, day, week]) # 5 min movement

        pass

    # in case different currencies don't cover the full dataset, removed for the moment
    # start = new_data[0][0][0]
    #
    # for i in range(1, len(new_data)):
    #     while new_data[i][0][0] != start:
    #         new_data[i].insert(0, [new_data[i][0][0] - 900000, 0,0,0,0,0,0,0,0,0,0])

    return new_data


def time_change_2(data, new_data, time):
    change = 0
    for _time in time:
        for i in range(len(data) - _time):
            change = (data[i + _time][1] / data[i][1]) - 1
            new_data[i + _time].append(change)
            pass
    del new_data[:time[-1]]
    return new_data

def time_change(data, time):
    _data = data.copy()

    for i in range(len(_data) - time):
        change = (_data[i + time][1] / _data[i][1]) - 1
        _data[i+time].append(change)
        pass
    for i in range(time):
        _data[i].append(0)
    return _data


def day_volume(data, day):
    _data = data.copy()

    for i in range(len(_data) - day): # appends the 24 hour volume to each timestamp
        volume = 0
        for x in range(day):
            volume += _data[i+x][2]
            pass
        _data[i+day].append(volume)
        pass

    for i in _data: # del the individual timestamp volume
        del i[2]

    for i in range(day):
        _data[i].append(_data[day][2]) # set the earlier timestamps to a normalized value

    return _data

def day_volume_movement(data, week, day):

    _data = data.copy()

    for i in range(len(data) - week):
        count = 0
        volume = 0

        for x in range(0, ((week*2)+1), day):
            if (i+x) < len(data):
                volume += data[i+x][2]
                count += 1

        volume_avg = volume / count

        _data[i+week].insert(3, ((data[i+week][2]/volume_avg) - 1) / 10)
        pass

    for i in range(week):
        _data[i].insert(3, 0.0)

    return _data


def inputs_full(data, time_interval):

    hour = int(60 / time_interval)
    _data = []

    for i in range(len(data[0])):
        _data.append([])
        for y in range(len(data)):
            for z in range(7):
                _data[i].append(data[y][i][z])
        pass

    # for i in _data:
    #     for x in range(3):
    #         i.append(0)
    #
    # # print('break')
    #
    # for i in range(len(data)):
    #     for y in range(len(data[i])):
    #         _data[y][1+i] = data[i][y][1]
    #
    #         for x in range(3, 7):
    #             _data[y].append(data[i][y][x])
    #
    # # save_file(_data, 't_inputs')

    return _data


def outputs(data, time_interval):

    hour = int(60/time_interval)
    _data = []

    for i in range(len(data[0]) - hour): # number of timestamps
        _data.append([])
        x = hour + i
        change = [0, 0, 0]
        for y in range(len(data)): # number of coins
            if data[y][i][1] != 0:
                change[y] = (data[y][x][1]/data[y][i][1]) - 1
            else:
                change[y] = 0
            pass
        winner = find_winner(change[0], change[1], change[2])
        for y in winner:
            _data[i].append(y)
        pass

    save_file(_data, 'outputs_zero')

    # save_file(_data_full, 'outputs_full')

    print('break')

    return _data


def find_winner(btc, eth, ltc):
    winner = [0, 0, 0]
    first = 1
    second = 0

    if btc > eth:
        if btc > ltc:
            winner[0] = first
        else:
            winner[0] = second
    else:
        if btc > ltc:
            winner[0] = second

    if eth > btc:
        if eth > ltc:
            winner[1] = first
        else:
            winner[1] = second
    else:
        if eth > ltc:
            winner[1] = second

    if ltc > btc:
        if ltc > eth:
            winner[2] = first
        else:
            winner[2] = second
    else:
        if ltc > eth:
            winner[2] = second

    return winner


def clean_inputs(data, time_interval):

    hour = int(60/time_interval)

    # _data = deepcopy(data)
    #
    # for i in _data:
    #     del i[:4]

    del data[-hour:]

    save_file(data, 'inputs')

    print('Break')

    return data


def build_file_list_bitfinex(currency):
    data = []

    for i in currency:
        _ = 'bitfinex_' + i + '_5min.csv'
        data.append(_)
        pass

    return data

def apply_scaler(data):

    _data = []
    scaler_data = [[],[],[]]

    for i in range(len(data)):
        _data.append([])
        series = [[], [], [], [], [], [], []]

        for y in range(len(data[i])):
            _data[i].append([])
            for x in range(7):
                _data[i][y].append(0)
                series[x].append(data[i][y][2+x])

        for x in range(7):
            scaler = MinMaxScaler(feature_range=(0, 1))
            _series = Series(series[x])
            values = _series.values
            values = values.reshape(len(values), 1)
            scaler = scaler.fit(values)
            normalized = scaler.transform(values)
            for y in range(len(_data[i])):
                _data[i][y][x] = (normalized[y][0])
                pass

            joblib.dump(scaler, ("scaler/scaler_" + str(i) + "_" + str(x)))

    print('break')

    return _data

def min_max(data, data_max, data_min):

    print('start min max')
    count1 = 0
    for i in data:
        count1 += 1
        print (str(count1))
        count_min = 0
        count_max = 0
        for y in i:

            for x in range(7):
                if y[x+2] > data_max[x]:
                    y[x+2] = data_max[x]
                    count_max += 1
                if y[x+2] < data_min[x]:
                    y[x+2] = data_min[x]
                    count_min += 1
                pass

            pass
        print(str(count_min))
        print(str(count_max))
        pass

    # save_file(data[0], 'btc_data_min_max')
    # save_file(data[1], 'eth_data_min_max')
    # save_file(data[2], 'ltc_data_min_max')

    # print("start charting")
    # count = 0
    #
    # for i in data:
    #     for x in range(2, 9):
    #         count += 1
    #         print("chart: " + str(count))
    #         _chart = []
    #         for y in i:
    #             _chart.append(y[x])
    #             pass
    #         y_pos = np.arange(len(_chart))
    #         plt = pg.plot(y_pos, _chart, title=str(count))
    #         exporter = pg.exporters.ImageExporter(plt.plotItem)
    #         _name = 'chart/' + str(count) + 'plot.png'
    #         exporter.export(_name)
    #         print('break')
    #         pass
    #     pass


    # for i in data:
    #     for x in range(2, 8):
    #         count += 1
    #         print("chart: " + str(count))
    #         _chart = []
    #         for y in i:
    #             _chart.append(y[x])
    #             pass
    #         y_pos = np.arange(len(_chart))
    #         plt.bar(y_pos, _chart, align='center', alpha=0.5)
    #         plt.savefig('chart/' + str(count) + 'plot.png', dpi=600)
    #         plt.close()
    #         print('break')
    #         pass
    #     pass

    print('break')

    return data
