#Dydx past balances
The purpose of this repo is to query Dydx(v1) balances historically from the Ethereum blockchain.

The market configuration that is set by Dydx is also hard coded in `dydx-past-balances/main.py`:

```
self.markets = {
             0: {'symbol': 'ETH', 'num': Wad.from_number(0)},
             1: {'symbol': 'SAI', 'num': Wad.from_number(1)},
             2: {'symbol': 'USDC', 'num': Wad.from_number(2)},
             3: {'symbol': 'DAI', 'num': Wad.from_number(3)}
         }
```


## Setup
```
git clone https://github.com/liquidityproviders/dydx-past-balances.git
cd dydx-past-balances
git submodule update --init --recursive
./install.sh
```
go to https://observablehq.com/@levity/search-for-a-block-by-timestamp and enter in the timestamp you would like Dydx balance data for

Enter in the block number returned by the link above into the start script below as the `--block-number-to-query` argument.

Ensure you have created the startfile, added it to the homedirectory of the repo (see example startfile below), and make sure it is executable.

create the `addresses_config.json` file in the repository's root directory, it should look something like this:
```
{
  "addresses": ["0x...","0x...","0x..."]
}
```

Run the startfile:

./start.sh


## Example start script
```
#!/bin/bash

source ./env
source ./_virtualenv/bin/activate || exit
dir="$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$dir:$dir/lib/pymaker

exec python3 -m dydx_past_balances.main \
    --rpc-host ${RPC_HOST:?} \
    --rpc-timeout 30 \
    --dydx-host 'https://api.dydx.exchange' \
    --addresses-config 'addresses_config.json' \
    --block-number-to-query 11566425 \
    $@ 2> >(tee -a ${LOGS_DIR:?}/dydx_past_balances.log >&2)
```

