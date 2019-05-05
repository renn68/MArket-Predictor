
import pandas as pd

import api_pull


START = 1493596800000  # 1496395200000, july 1st 2017 0000
END = 1538265600000  # july 1st, 2018 0000
# END = 1501916000000 # test value

XRP_START = 1496275200000
BCH_START = 1501891200000
EOS_START = 1500076800000
IOTA_START = 1500076800000
NEO_START = 1500076800000

start = START
end = END

currency = ["BTCUSD", "ETHUSD", "LTCUSD", "ZECUSD", "XMRUSD", "DSHUSD", "XRPUSD", "BCHUSD", "EOSUSD", "IOTUSD", "NEOUSD"]
# currency = ["BTCUSD", "ETHUSD", "LTCUSD"]
params = { 'start' : start, 'end' : end, 'limit' : 1000, 'sort' : 1 }
url = "https://api.bitfinex.com/v2/candles/trade:5m:t"


for x in range(len(currency)):

    params = {'start': start, 'end': end, 'limit': 1000, 'sort': 1}

    if currency[x] == "XRPUSD":
        params['start'] = XRP_START

    if currency[x] == "BCHUSD":
        params['start'] = BCH_START

    if currency[x] == "EOSUSD":
        params['start'] = EOS_START

    if currency[x] == "IOTUSD":
        params['start'] = IOTA_START

    if currency[x] == "NEOUSD":
        params['start'] = NEO_START

    _url = url + currency[x] + chr(47) + "hist"

    d = api_pull.api_request(_url, params, 6, start, end)

    df = pd.DataFrame(d)
    df.to_csv('data/bitfinex_' + currency[x] + '_5min.csv', index=False, header=False)

    pass