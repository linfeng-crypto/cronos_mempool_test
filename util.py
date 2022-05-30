import os
import json
import web3

from dotenv import load_dotenv
from eth_account import Account
from pathlib import Path
from solcx import compile_source, install_solc
from pystarport import ports
from web3._utils.transactions import fill_nonce, fill_transaction_defaults

try:
    install_solc(version='latest')
except:
    pass
load_dotenv(Path(__file__).parent / "scripts/.env")
Account.enable_unaudited_hdwallet_features()
ACCOUNTS = {
    "validator": Account.from_mnemonic(os.getenv("VALIDATOR1_MNEMONIC")),
    "community": Account.from_mnemonic(os.getenv("COMMUNITY_MNEMONIC")),
    "signer1": Account.from_mnemonic(os.getenv("SIGNER1_MNEMONIC")),
    "signer2": Account.from_mnemonic(os.getenv("SIGNER2_MNEMONIC")),
}
ADDRS = {name: account.address for name, account in ACCOUNTS.items()}

class Cronos:
    def __init__(self, base_dir):
        self._w3 = None
        self.base_dir = base_dir
        self.config = json.loads((base_dir / "config.json").read_text())
        self.enable_auto_deployment = json.loads(
            (base_dir / "genesis.json").read_text()
        )["app_state"]["cronos"]["params"]["enable_auto_deployment"]
        self._use_websockets = False

    def copy(self):
        return Cronos(self.base_dir)

    @property
    def w3_http_endpoint(self, i=0):
        port = ports.evmrpc_port(self.base_port(i))
        return f"http://localhost:{port}"

    @property
    def w3_ws_endpoint(self, i=0):
        port = ports.evmrpc_ws_port(self.base_port(i))
        return f"ws://localhost:{port}"

    @property
    def w3(self):
        if self._w3 is None:
            if self._use_websockets:
                self._w3 = web3.Web3(
                    web3.providers.WebsocketProvider(self.w3_ws_endpoint)
                )
            else:
                self._w3 = web3.Web3(web3.providers.HTTPProvider(self.w3_http_endpoint))
        return self._w3

    def base_port(self, i):
        return self.config["validators"][i]["base_port"]

    def node_rpc(self, i):
        return "tcp://127.0.0.1:%d" % ports.rpc_port(self.base_port(i))

    def use_websocket(self, use=True):
        self._w3 = None
        self._use_websockets = use


def sign_transaction(w3, tx, key="validator"):
    "fill default fields and sign"
    acct = ACCOUNTS[key]
    tx["from"] = acct.address
    tx = fill_transaction_defaults(w3, tx)
    tx = fill_nonce(w3, tx)
    return acct.sign_transaction(tx)


def send_transaction(w3, tx, key="validator"):
    signed = sign_transaction(w3, tx, key)
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.eth.wait_for_transaction_receipt(txhash)


def deploy_contract(w3, sol_file):
    def compile_sol():
        with open(sol_file) as f:
            contract_str = f.read()
            compiled_sol = compile_source(contract_str,  output_values=['abi', 'bin'])
            contract_id, contract_interface = compiled_sol.popitem()
            bytecode = contract_interface['bin']
            abi = contract_interface['abi']
            return [bytecode, abi]
    [bin, abi] = compile_sol()
    w3.eth.default_account = w3.eth.accounts[0]
    contract = w3.eth.contract(abi=abi, bytecode=bin)
    tx_hash = contract.constructor().transact()
    txreceipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert txreceipt.status == 1
    address = txreceipt.contractAddress
    print(f"deploy contract success, contract address: {address}")
    return w3.eth.contract(address=address, abi=abi)
