import json
import os
import requests
from brownie import Contract
from dotenv import load_dotenv
load_dotenv()


def load_contract(provider, address, chain='mainnet', saved_abi=False, proxy_addr=False):
    if saved_abi:
        abi = json.load(open(saved_abi, 'r'))
    else:
        if proxy_addr:
            abi = get_abi(proxy_addr, chain)
        else:
            abi = get_abi(address, chain)

    contract = provider.eth.contract(abi=abi, address=address)

    return contract


def get_abi(address, chain):
    if chain == 'mainnet':
        api = os.getenv('ETHERSCAN_API')
        path = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={api}'
    elif chain == 'optimism':
        api = os.getenv('OPT_ETHERSCAN_API')
        path = f'https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={api}'
    elif chain == 'arbitrum':
        api = os.getenv('ARBITRUM_ETHERSCAN_TOKEN')
        path = f'https://api.arbiscan.io/api?module=contract&action=getabi&address={address}&apikey={api}'
    else:
        raise ValueError(f'unknown chain {chain}')

    abi = json.loads(requests.get(path).json()['result'])
    return abi

def load_brownie_contract(address, chain='mainnet', saved_abi=False, proxy_addr=False):
    """
    Loads Brownie contract object from address and abi file name
    :param address :(str) Contract address
    :param abi_file:(str) Abi file name (path included)
    :return: Brownie Contract Obj
    """
    if saved_abi:
        with open(saved_abi, 'r') as file:
            abi = json.load(file)
    else:
        if proxy_addr:
            abi = get_abi(proxy_addr, chain)
        else:
            abi = get_abi(address, chain)

    contract = Contract.from_abi(name='contract',address = address, abi = abi)

    return contract
    