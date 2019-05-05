import geth_settings, geth_util
import time, requests
from web3 import Web3
import numpy as py
import pandas as pd




class Horses:
    def __init__(self):
        
        self.etherscan_key = geth_settings.etherscan_key
        self.url_factory_topic = geth_settings.url_factory_topic
        self.url_race_bet_topic = geth_settings.url_race_bet_topic
        self.contract_factory_address = geth_settings.contract_factory_address


        self.current_unix = time.time()
        self.from_block = 5117393

        self.open_races = []
        self.running_races = []
        self.finished_races = []

        self.load_race_history()

        self.read_events(self.from_block)

        pass

    def read_events(self, from_block):
        url = self.etherscan_race_request(from_block, self.url_factory_topic, self.contract_factory_address)
        time.sleep(0.2)
        log = requests.get(url)
        log_text = log.json()
        log_text_data = []
        for i in log_text['result']:
            log_text_data.append(self.normalize_data(i['data']))
        self.sort_races(log_text_data)
        pass

    def sort_races(self, races):
        count = 1
        for race in races:
            print(count)
            count += 1
            if race['time'] + race['betting_duration'] > self.current_unix:  # check if open race
                if (race['address'] in self.open_races) is False:
                    self.open_races.append(self.get_betting_info(race))
                    pass
                pass
            elif (race['time'] + race['betting_duration'] < self.current_unix) and (race['time'] + race['betting_duration'] + race['race_duration'] > self.current_unix):  # check if running race
                if (race['address'] in self.running_races) is False:
                    self.running_races.append(self.get_betting_info(race))
                pass
            else:
                if (race['address'] in self.finished_races) is False:  # check if closed race
                    self.finished_races.append(self.get_betting_info(race))
            pass
        pass

    def get_betting_info(self, race):
        url = self.etherscan_race_request(self.from_block, self.url_race_bet_topic, race['address'])
        log = requests.get(url)
        log_text = log.json()
        return race

    def normalize_data(self, text):
        data = dict()
        _text = list(text)
        del _text[:2]
        _ = []
        for i in range(5):
            _.append([])
            for x in range(64):
                _[i].append(_text[(i * 64) + x])
                pass
            pass
        data['address'] = self.hex_to_address(_[0])
        data['address_factory'] = self.hex_to_address(_[1])
        data['betting_duration'] = Web3.toInt(hexstr=''.join(_[2]))
        data['race_duration'] = Web3.toInt(hexstr=''.join(_[3]))
        data['time'] = Web3.toInt(hexstr=''.join(_[4]))
        data['BTC'] = 0.001
        data['ETH'] = 0.001
        data['LTC'] = 0.001
        data['total_bet'] = 0.0
        data['BTC_odds'] = 0.0
        data['ETH_odds'] = 0.0
        data['LTC_odds'] = 0.0
        data['winner'] = ""
        return data

    def hex_to_address(self, hex):
        address = "0x"
        del hex[:24]
        address = address + ''.join(hex)
        address = Web3.toChecksumAddress(address)
        return address

    def etherscan_race_request(self, from_block, topic, address):
        _url = ['https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=',
                '&toBlock=latest&address=',
                '&topic0=',
                '&apikey=']

        url = _url[0] + str(from_block) + _url[1] \
              + address \
              + _url[2] + topic + \
              _url[3] + self.etherscan_key

        return url
    
    def etherscan_recent_block(self, hours):
        url = "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey="
        url = url + self.etherscan_key
        block = requests.get(url)
        block = block.json()
        block = Web3.toInt(hexstr=block['result'])
        day_sec = 60 * 60 * hours  # 86400 seconds per day
        blocks_per_day = round(day_sec / 14)  # est. 14 sec per block
        return block - (blocks_per_day)

    def save_race_history(self):
        df = pd.DataFrame.from_dict(self.finished_races)
        df.to_csv('data/finished_races.csv', index=None)
        pass

    def load_race_history(self):
        df = pd.read_csv("data/finished_races.csv")
        a = df.values.tolist()
        self.finished_races = df.to_dict(orient='records')
        self.finished_races = [race for race in self.finished_races]
        pass


if __name__ == "__main__":

    races = Horses()
    races.save_race_history()

    print('Break')

    pass
