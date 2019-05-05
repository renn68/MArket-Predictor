import pandas as pd

from os import listdir
from os.path import isfile, join

import util

# currency = ["BTCUSD", "ETHUSD", "LTCUSD", "ZECUSD", "XMRUSD", "DSHUSD", "XRPUSD", "BCHUSD", "EOSUSD", "IOTUSD", "NEOUSD"]

currency = ["BTCUSD", "ETHUSD", "LTCUSD"]  # currencies used for the data set
path = "data/" # Directory with the raw api data
time_interval = 5 # set the time range of the dataset


files_list = util.build_file_list_bitfinex(currency) # generate a list of file names

data = dict()

data_max = [0.04, 0.06, 0.08, 0.1, 0.1, 0.2, 0.4]
data_min = [-0.04, -0.06, -0.08, -0.1, -0.1, -0.2, -0.4]




data = util.generate(files_list, path) # returns a dict of the raw data


data = util.fill_dates(data, currency, time_interval) # fill any missing timestamps, and break data into 3 main stats, Time, Close Price, Volume

new_data = []


new_data = util.build_price_movements_2(data, currency, time_interval)  # format (timestamp, price, 5min, 10min, 15min, 20min, 1hr, 1day, 1 week)

# new_data = util.build_price_movements(data, currency, time_interval)
#

new_data = util.min_max(new_data, data_max, data_min)


new_data_scaled = []
new_data_scaled = util.apply_scaler(new_data)



inputs_full = util.inputs_full(new_data_scaled, time_interval)


outputs = util.outputs(new_data, time_interval)

inputs = util.clean_inputs(inputs_full, time_interval)

print('finished')
