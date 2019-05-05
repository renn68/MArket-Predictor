from web3 import Web3
import geth_settings

def normalize_data(text):
    data = dict()
    _text = list(text)
    del _text[:2]
    _ = []
    for i in range(5):
        _.append([])
        for x in range(64):
            _[i].append(_text[(i*64)+x])
            pass
        pass

    data['address'] = hex_to_address(_[0])
    data['address_factory'] = hex_to_address(_[1])
    data['betting_duration'] = Web3.toInt(hexstr=''.join(_[2]))
    data['race_duration'] = Web3.toInt(hexstr=''.join(_[3]))
    data['time'] = Web3.toInt(hexstr=''.join(_[4]))

    return data


def hex_to_address(hex):
    address = "0x"
    del hex[:24]
    address = address + ''.join(hex)
    address = Web3.toChecksumAddress(address)
    return address


url = (
    'https://api.etherscan.io/api?module=logs&action=getLogs'
    '&fromBlock=6100007&toBlock=latest'
    '&address=0x028377b5D7eFC17C8450c70444C17ab317109f5f'
    '&topic0=0x45e0d982769d602d7f7b87a4d6dceb2aa2b124de1162f549984cf1e60ae29919'
    '&apikey=api-key'
    )


def etherscan_url(from_block):
    _url = ['https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=',
            '&toBlock=latest&address=',
            '&topic0=',
            '&apikey=']

    url = _url[0] + str(from_block) + _url[1] + geth_settings.url_address \
          + _url[2] + geth_settings.url_topic + \
          _url[3] + geth_settings.etherscan_key

    return url
