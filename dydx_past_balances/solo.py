


from pymaker import Address, Contract, Wad
from web3 import Web3
from typing import Optional
from pprint import pprint


class Solo(Contract):

    abi = Contract._load_abi(__name__, 'abi/Solo.abi')
    bin = Contract._load_bin(__name__, 'abi/Solo.bin')

    def __init__(self, web3: Web3, address: Address):
        assert(isinstance(web3, Web3))
        assert(isinstance(address, Address))

        self.web3 = web3
        self.address = address
        self._contract = self._get_contract(web3, self.abi, address)

    def get_account_wei(self, account: Address, acc_num: Wad, market_id: Wad):
        assert isinstance(account, Address)
        assert isinstance(market_id, Wad)
        assert isinstance(acc_num, int)

        try:
            data = self._contract.functions.getAccountWei((account.address, acc_num), market_id.value).call()
            return (data[0], data[1]/ 10**18)

        except ValueError:
            return (False, 0.0)

    def get_account_balances(self, account: Address, acc_num: Wad, block_number: Optional[int]):
        assert isinstance(block_number, int) or (block_number is None)
        assert isinstance(account, Address)
        assert isinstance(acc_num, int)


        return_obj = {}

        if block_number:
            return_data = self._contract.functions.getAccountBalances((account.address, acc_num)).call(block_identifier=block_number)

        else:
            return_data = self._contract.functions.getAccountBalances((account.address, acc_num)).call()

        for i, val in enumerate(return_data):
            for inner_i, inner_val in enumerate(val):

                if i == 0:
                    return_obj[inner_i] = {'token_address': val[inner_i]}
                elif i == 1:
                    return_obj[inner_i]['principal'] = val[inner_i][1]/10**18
                else:
                    if inner_i == 2:
                        return_obj[inner_i]['total_bal'] = val[inner_i][1]/10**6
                    else:
                        return_obj[inner_i]['total_bal'] = val[inner_i][1]/10**18

        return return_obj





