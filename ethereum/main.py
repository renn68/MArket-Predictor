import time
# from web3 import Web3, HTTPProvider, IPCProvider, eth
import contract_abi, contract_factory_abi
import requests, geth_settings

from etherscan_horse import Horses

import geth_util

# w3 = Web3(HTTPProvider(settings.infura_api))
# contract_factory = w3.eth.contract(address = settings.contract_factory_address, abi = contract_factory_abi.abi)
# contract = w3.eth.contract(address = settings.contract_address, abi = contract_abi.abi)

current_unix = time.time()
from_block = geth_settings.from_block

'''
def send_ether_to_contract(amount_in_ether):
    amount_in_wei = w3.toWei(amount_in_ether,'ether');
    nonce = w3.eth.getTransactionCount(settings.wallet_address)
    transaction = {
            'value': amount_in_wei,
            'gasPrice': Web3.toWei('6', 'gwei'),
            'gas': 100000,
            'nonce': nonce,
    }

    txn_dict = contract.functions.placeBet(Web3.toBytes(text='ETH')).buildTransaction(transaction)

    signed_txn = w3.eth.account.signTransaction(txn_dict, settings.wallet_private_key)

    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
        print(txn_receipt)
        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'txn_receipt': txn_receipt}
'''

# send_ether_to_contract(0.01)

races = Horses()

print('break')
