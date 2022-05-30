import time
from pprint import pprint
from pathlib import Path
from util import ADDRS, sign_transaction, deploy_contract, Cronos
import threading


class Runner(object):
    contract_txs = []
    transfer_token_txs = []
    total_contract_txs = 0
    total_transfer_token_txs = 0

    def __init__(self, cronos, tx_numbers, sol_file):
        self.tx_numbers = tx_numbers
        self.cronos = cronos
        self._contract = None
        self.sol_file = sol_file
        self.contract_gas_limit = 400000
        self.tx_gas_limit = 200000
        self._w3 = None

    @property
    def w3(self):
        if not self._w3:
            self._w3 = self.cronos.w3
            # self._w3.eth.default_account = ACCOUNTS["validator"]
        return self._w3

    @property
    def contract(self):
        if self._contract:
            return self._contract
        else:
            contract = deploy_contract(
                self.cronos.w3,
                self.sol_file,
            )
            self._contract = contract
            return contract

    def run_contract(self, keys=["validator", "community"]):
        for key in keys:
            sender = ADDRS[key]
            nonce_start = self.w3.eth.get_transaction_count(sender)

            def _set_greeting(nonce):
                tx = self.contract.functions.setGreeting("abc").buildTransaction(
                    # TODO: set gasPrice instead of using the default
                    {
                        "from": sender,
                        "nonce": nonce,
                        "gas": self.contract_gas_limit
                    }
                )
                signed = sign_transaction(self.w3, tx, key)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                return tx_hash

            for i in range(self.tx_numbers):
                try:
                    nonce = nonce_start + i
                    tx_hash = _set_greeting(nonce)
                    self.contract_txs.append(tx_hash)
                    self.total_contract_txs += 1
                    time.sleep(0.01)
                except Exception as e:
                    print("send contract tx error:",  e)
                    break


    def transfer_tokens(self, keys=["signer1", "signer2"]):
        # gas_price = self.w3.eth.gas_price
        for key in keys:
            sender = ADDRS[key]
            nonce_start = self.w3.eth.get_transaction_count(sender)
            def _transfer(nonce):
                tx = {
                    "to": "0x0000000000000000000000000000000000000000",
                    "value": 10,
                    "gas": self.tx_gas_limit,
                    "nonce": nonce,
                }
                signed = sign_transaction(self.w3, tx, key)
                txhash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                return txhash

            for i in range(self.tx_numbers):
                try:
                    nonce = nonce_start + i
                    txhash = _transfer(nonce)
                    self.total_transfer_token_txs += 1
                    self.transfer_token_txs.append(txhash)
                    time.sleep(0.01)
                except Exception as e:
                    print("send normal tx error: ", e)
                    break

    def check_status(self):
        default_status = {}
        last_height = self.w3.eth.block_number
        last_block = self.w3.eth.get_block('latest')
        while True:
            current_height = self.w3.eth.block_number
            if current_height > last_height:
                current_block = self.w3.eth.get_block('latest')
                mined_txs = current_block.transactions
                for tx in mined_txs:
                    try:
                        self.contract_txs.remove(tx)
                    except:
                        pass
                    try:
                        self.transfer_token_txs.remove(tx)
                    except:
                        pass
                status = default_status
                # check txs in block
                time_delta = current_block["timestamp"] - last_block["timestamp"]
                status["current_height"] = current_height
                status["block_time_use"] = f"{time_delta}s"
                status["mempool_normal_txs"] = len(self.transfer_token_txs)
                status["mempool_contract_txs"] = len(self.contract_txs)
                status["mempool_total_txs"] = len(self.transfer_token_txs) + len(self.contract_txs)
                status["block_gas_limit"] = current_block.gasLimit
                status["block_gas_used"] = f"{current_block.gasUsed} ({current_block.gasUsed*100.0/current_block.gasLimit}%)"
                status["block_txs"] = len(mined_txs)
                pprint(status)
                last_height = current_height
                last_block = current_block
            time.sleep(1)

def test():
    data_path = Path("./cronos_data")
    cronos = Cronos(data_path / "cronos_777-1")
    runner = Runner(cronos, tx_numbers=100000, sol_file="./scripts/greeting.sol")
    t1 = threading.Thread(target=runner.transfer_tokens)
    t1.start()
    t2 = threading.Thread(target=runner.run_contract)
    t2.start()
    runner.check_status()

if __name__ == "__main__":
    test()

