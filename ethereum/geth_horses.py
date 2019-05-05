import geth_settings, geth_util, contract_factory_abi, contract_abi
import time, requests
from web3 import Web3, IPCProvider, eth, WebsocketProvider, HTTPProvider
import pandas as pd
import msvcrt

class Horses:
    def __init__(self):
        self.wallet_private = geth_settings.wallet_private_key
        self.wallet_address = geth_settings.wallet_address

        self.unix_time = time.time()
        self.timezone_add = 3 * 3600
        self.current_gas = 0
        self.count = 0
        self.bet_amount = 0.01

        self.races = []


        self.contract_factory_address = geth_settings.contract_factory_address

        self.load_race_history()

        self.from_block = Web3.toHex(int(geth_settings.from_block))

        self.w3 = Web3()

        self.contract_factory = self.w3.eth.contract(address=self.contract_factory_address, abi = contract_factory_abi.abi)

        self.created_races()
        self.check_finished_races()

        self.gas_price = self.get_gas_price()



        pass
    
    def get_gas_price(self):
        gas = requests.get("https://api.etherscan.io/api?module=proxy&action=eth_gasPrice&apikey=" + geth_settings.etherscan_key)
        gas = gas.json()
        return  (Web3.toInt(hexstr=gas['result']) / 1000000000) + 6.1

    def created_races(self):
        new_races_filter = self.contract_factory.events.RaceDeployed.createFilter(fromBlock=self.from_block)
        log = new_races_filter.get_all_entries()
        for race in log:
            self.parse_race(race)
        pass

    def parse_race(self, race):
        if (race['args']['_address'] in (_race['address'] for _race in self.races)) is False:
            self.races.append(self.get_betting_info(race))
            pass

        pass

    def get_betting_info(self, race):
        data = {}
        data['address'] = race['args']['_address']
        data['address_factory'] = self.contract_factory_address
        data['betting_duration'] = race['args']['_bettingDuration']
        data['race_duration'] = race['args']['_raceDuration']
        data['time'] = race['args']['_time']
        data['BTC'] = 0.001
        data['ETH'] = 0.001
        data['LTC'] = 0.001
        data['total_bet'] = 0.0
        data['BTC_odds'] = 0.0
        data['ETH_odds'] = 0.0
        data['LTC_odds'] = 0.0
        data['bet_placed'] = False
        data['finished'] = False
        data['winner'] = ""

        print(data['address'])
        data = self.read_race_data(data)

        return data
    
    def check_finished_races(self):
        if self.races:
            for race in self.races:
                if race['time'] + race['betting_duration'] < self.unix_time:
                    race['finished'] = True
            pass
        pass

    def read_race_data(self, race):

        print(self.count)
        self.count += 1
        contract_race = self.w3.eth.contract(address=race['address'], abi = contract_abi.abi)
        races_filter = contract_race.events.Deposit.createFilter(fromBlock=self.from_block)
        logs = races_filter.get_all_entries()

        race['BTC'] = 0.001
        race['ETH'] = 0.001
        race['LTC'] = 0.001
        race['total_bet'] = 0.0

        for log in logs:
            if log['args']['_horse'][:3] == Web3.toBytes(text='BTC'):
                race['BTC'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
                race['total_bet'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
            elif log['args']['_horse'][:3] == Web3.toBytes(text='ETH'):
                race['ETH'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
                race['total_bet'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
            elif log['args']['_horse'][:3] == Web3.toBytes(text='LTC'):
                race['LTC'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
                race['total_bet'] += float(Web3.fromWei(log['args']['_value'], 'ether'))
            else:
                print('parsing bets, found a bet without btc, eth, ltc')

            _total = race['total_bet'] * 0.925

            race['BTC_odds'] = _total / race['BTC']
            race['ETH_odds'] = _total / race['ETH']
            race['LTC_odds'] = _total / race['LTC']

            if contract_race.functions.winner_horse(b'BTC').call():
                race['winner'] = 'BTC'
            elif contract_race.functions.winner_horse(b'ETH').call():
                race['winner'] = 'ETH'
            elif contract_race.functions.winner_horse(b'LTC').call():
                race['winner'] = 'LTC'
            else:
                race['winner'] = 'NA'
            pass
        return race

    def save_race_history(self):
        df = pd.DataFrame.from_dict(self.races)
        df.to_csv('data/finished_races.csv', index=None)
        print("saved")
        pass

    def load_race_history(self):
        try:
            df = pd.read_csv("data/finished_races.csv")
            a = df.values.tolist()
            self.races = df.to_dict(orient='records')
            self.races = [race for race in self.races]
        except:
            print("no existing file")
        pass

    def open_race_log(self, race):
        _time = pd.to_datetime(race['time'] + race['betting_duration'] + self.timezone_add, unit='s')
        print("race starts at: ", _time)
        print("Bets - BTC: {:.2f}  ETH: {:.2f}  LTC: {:.2f}  Total : {:.2f}".format(race['BTC'], race['ETH'], race['LTC'], race['total_bet']))
        print("Odds - BTC: {:.2f}  ETH: {:.2f}  LTC: {:.2f}".format(race['BTC_odds'], race['ETH_odds'], race['LTC_odds']))
        print("\n")

    def update_open_races(self):
        self.gas_price = self.get_gas_price()
        self.update_time()
        self.created_races()
        for race in self.races:
            if not race['finished']:
                print(self.gas_price)
                self.read_race_data(race)
                self.open_race_log(race)
                self.check_place_bet(race)
            pass

    def quick_check(self):
        _time = pd.to_datetime(time.time() + self.timezone_add, unit='s')
        print("check: ", _time)
        time.sleep(10)
        self.update_time()
        for race in self.races:
            if not race['finished']:
                self.check_place_bet(race)

        pass

    def check_place_bet(self, race):
        if not race['finished']:
            if not race['bet_placed']:
                if race['time'] + race['betting_duration'] < self.unix_time + 40:
                    self.place_bet(race)
                    print('place bet')
                    pass
                pass
            pass

    def update_time(self):
        self.unix_time = time.time()

    def place_bet(self, race):

        race['bet_placed'] = True
        race['finished'] = True

        contract = self.w3.eth.contract(address=race['address'], abi = contract_abi.abi)
        amount_in_wei = self.w3.toWei(self.bet_amount, 'ether');
        nonce = self.w3.eth.getTransactionCount(geth_settings.wallet_address)
        transaction = {
            'value': amount_in_wei,
            'gasPrice': Web3.toWei(str(self.gas_price), 'gwei'),
            'gas': 150000,
            'nonce': nonce,
        }

        bet = 'ETH'
        if race['BTC'] < race['ETH'] and race['BTC'] < race['LTC']:
            bet = 'BTC'
        if race['ETH'] < race['BTC'] and race['ETH'] < race['LTC']:
            bet = 'ETH'
        if race['LTC'] < race['ETH'] and race['LTC'] < race['BTC']:
            bet = 'LTC'

        print(bet)

        txn_dict = contract.functions.placeBet(Web3.toBytes(text=bet)).buildTransaction(transaction)

        signed_txn = self.w3.eth.account.signTransaction(txn_dict, geth_settings.wallet_private_key)

        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        txn_receipt = None
        count = 0
        while txn_receipt is None and (count < 60):
            txn_receipt = self.w3.eth.getTransactionReceipt(txn_hash)
            print(txn_receipt)
            time.sleep(5)

        self.save_race_history()
        if txn_receipt is None:
            print('transaction failed')
        pass


if __name__ == "__main__":
    races = Horses()

    races.save_race_history()

    try:
        while True:
            races.update_open_races()
            for i in range(60):
                races.quick_check()
                pass
        pass
    except KeyboardInterrupt:
        races.save_race_history()
        pass


    pass
