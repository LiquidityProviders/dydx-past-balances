

import sys
import json
import requests
import argparse
from dydx_past_balances.solo import Solo
from web3 import Web3, HTTPProvider
from pprint import pprint
from pymaker import Address, web3_via_http, Wad
from pymaker.util import hexstring_to_bytes
from eth_utils.hexadecimal import decode_hex


class DydxHistoricBalances:

    def __init__(self, args: list):
        parser = argparse.ArgumentParser(prog='dydx-historic-balances')

        parser.add_argument("--rpc-host", type=str, default="http://localhost:8545",
                            help="JSON-RPC endpoint URI with port (default: `http://localhost:8545')")

        parser.add_argument("--rpc-timeout", type=int, default=10,
                            help="JSON-RPC timeout (in seconds, default: 10)")

        parser.add_argument("--dydx-host", type=str, default="https://api.dydx.exchange",
                            help="DYDX endpoint URI with port (default: 'https://api.dydx.exchange')")

        parser.add_argument("--addresses-config", required=True, type=argparse.FileType('r'),
                            help="configuration file to identify DYDX addresses.")

        parser.add_argument('--block-number-to-query', type=int, default=None,
                            help="block from which to pull at historical Dydx balances")


        self.arguments = parser.parse_args(args)
        self.dydx_endpoint = self.arguments.dydx_host
        self.block_number = self.arguments.block_number_to_query
        self.web3 = Web3(HTTPProvider(endpoint_uri=self.arguments.rpc_host))
        print(f"URL (Ethereum Node) Endpoint - {self.arguments.rpc_host}")
        print(f"Client Verion - {self.web3.clientVersion} ")
        print(f"The blocknumber where balances are requested: {self.block_number}")

        self.markets = {
            0: {'symbol': 'ETH', 'num': Wad.from_number(0)},
            1: {'symbol': 'SAI', 'num': Wad.from_number(1)},
            2: {'symbol': 'USDC', 'num': Wad.from_number(2)},
            3: {'symbol': 'DAI', 'num': Wad.from_number(3)}
        }

        loaded_addresses = json.loads(self.arguments.addresses_config.read())['addresses']
        self.addresses = map(lambda n: Address(n), loaded_addresses)

        # Solo mainnet contract address available here:
        # https://github.com/dydxprotocol/solo/blob/aeac02862d079d0bc5a984f56d2b9942c9ce41b9/migrations/deployed.json#L8
        self.solo = Solo(self.web3, Address('0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e'))


    def _get_acc_nonce(self, address):
        assert isinstance(address, Address)

        response = requests.get(f'{self.dydx_endpoint}/v1/accounts/{address}')

        if not response.ok:
            error_msg = f"{response.status_code} {response.reason} ({response.text})"
            raise RuntimeError(f"Query failed: {error_msg}")

        result = json.loads(response.text)

        return int(result['accounts'][0]['number'])


    def _combine_acc_data(self, margin_data, spot_data, markets, total_obj):

        acc_data = {}
        for market in margin_data:
            acc_data[markets[market]['symbol']] = {
                    'token_address': margin_data[market]['token_address'],
                    'balance':  margin_data[market]['total_bal'] + spot_data[market]['total_bal']
                    }
            if total_obj.get(markets[market]['symbol']):
                total_obj[markets[market]['symbol']] += (margin_data[market]['total_bal'] + spot_data[market]['total_bal'])
            else:
                total_obj[markets[market]['symbol']] = (margin_data[market]['total_bal'] + spot_data[market]['total_bal'])


        return acc_data, total_obj


    def main(self):
        return_obj = {}
        total_obj = {}

        for address in self.addresses:
            acc_nonce = self._get_acc_nonce(address)

            margin_acc = self.solo.get_account_balances(address, Wad.from_number(0).value, self.block_number)
            spot_acc = self.solo.get_account_balances(address, acc_nonce, self.block_number)
            return_obj[address],total_obj = self._combine_acc_data(margin_acc, spot_acc, self.markets, total_obj)



        pprint(return_obj)
        print(f"// TOTAL// :")
        pprint(total_obj)


if __name__ == '__main__':
    DydxHistoricBalances(sys.argv[1:]).main()
