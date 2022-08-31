# quantent

Public repo for various Brahma Quant Content

## Structure
- [data/](https://github.com/Brahma-fi/quantent/tree/main/data) Contains any data files as well as pre-downloaded contract ABIs
- [modules/](https://github.com/Brahma-fi/quantent/tree/main/modules) Contains all classes as well as useful utility and helper functions
- [notebooks/](https://github.com/Brahma-fi/quantent/tree/main/notebooks) Contains juptyer notebook files used for data analysis

## Setup
This repo uses Python's [eth-brownie](https://eth-brownie.readthedocs.io/) package extensively in order to query blockchain data. 

To query live networks one can make use of web3 infrastructure providers such as Infura or Alchemy. You will need to save your API key in a .env file under the variable name ``WEB3_ALCHEMY_PROJECT_ID`` or ``WEB3_INFURA_PROJECT_ID``. Brownie ships with the default provider set to Infura. To change provider, run the below in terminal:

``
$ brownie networks set_provider alchemy
``

For more Brownie network help, please refer to their [docs](https://eth-brownie.readthedocs.io/en/latest/network-management.html)

### Etherscan APIs
Etherscan APIs are also used to fetch contract ABIs removing the need to continually have to save them locally. The API tokens also need to be saved in your .env file. ``ETHERSCAN_TOKEN`` for [Mainnet](https://etherscan.io/), ``OPT_ETHERSCAN_TOKEN`` for [Optimism](https://optimistic.etherscan.io/) and ``ARBITRUM_ETHERSCAN_TOKEN`` for [Arbitrum](https://arbiscan.io/) 
