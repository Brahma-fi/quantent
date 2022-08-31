import pandas as pd

from brownie import multicall, network, web3
from modules.utils import load_brownie_contract
from modules.perp_constants import PERP_ADDRESSES, TOKENS
from dotenv import load_dotenv
load_dotenv()


class Perp:
    
    def __init__(self):
        if not network.is_connected():
            network.connect('optimism-main')
            
        self.bn = web3.eth.block_number
        self.chain = 'optimism'
        self.abi_path = '../data/ABIs/'
        self.erc20_abi = self.abi_path+'erc20_abi.json'
        self.base_token_abi = self.abi_path+'perp_base_token_abi.json'
        self.univ3_abi = self.abi_path+'univ3_pool_abi.json'
        
        self.registry = load_brownie_contract(PERP_ADDRESSES['market_registry'], 
                                              chain=self.chain,
                                              saved_abi=False,
                                              proxy_addr=PERP_ADDRESSES['market_reg_proxy'])
        
        self.v_usd = load_brownie_contract(PERP_ADDRESSES['v_usd'], 
                                           chain=self.chain,
                                           saved_abi=self.erc20_abi)
        
        self.decimals = self.v_usd.decimals()

        self.pool_data = self.get_pool_data(TOKENS)
    
    def get_pool_data(self, tokens):
        
        with multicall:
            token_contracts = [load_brownie_contract(token, chain=self.chain, saved_abi=self.base_token_abi) for token in tokens]
            symbols = [str(token_contract.symbol()) for token_contract in token_contracts]
            index_prices = [token_contract.getIndexPrice(15) for token_contract in token_contracts]

            pool_addresses = [self.registry.getPool(token) for token in tokens]    
            pool_balances = [(token_contract.balanceOf(pool_addr), self.v_usd.balanceOf(pool_addr)) for token_contract, pool_addr in zip(token_contracts, pool_addresses)]

            pool_contracts = [load_brownie_contract(addr, chain=self.chain, saved_abi=self.univ3_abi) for addr in pool_addresses]
            pool_details = [(contract.slot0(), contract.liquidity()) for contract in pool_contracts]
            
        columns = ['index_price', 'mark_price', 'pool_tvl', 'pool_liquidity']
        pool_data = pd.DataFrame(index=symbols, columns=columns)

        for i in range(0, len(tokens)):
            price_sqrtx96 = pool_details[i][0][0]
            price = round((price_sqrtx96 / (2**96))**2, 3)
            liquidity = pool_details[i][1] / 10**self.decimals
            index_price = round(index_prices[i] / 10**self.decimals, 3)
            tvl = pool_balances[i][0]/10**self.decimals*index_price+pool_balances[i][1]/10**self.decimals

            pool_data.loc[symbols[i], columns] = [index_price, price, tvl, liquidity]

        return pool_data.astype(float)
