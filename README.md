# Cronos Stress Test
This test cause is used to tress test the mempool, sending token transfer tx and contract tx and watch the mempool status and block mined time.

# start
1. init cronos: `sh init_cronos.sh`
2. start cronosd: `pystarport start --data ./cronos_data`
3. start the stress test: `python3 main.py`

# test result
mempool will full when the pending transactions up to nearly 5000, send tx will get error message: `mempool is full`
what ever how many pending transaction is, the block mined time is always 5s or 6s which is same as set by `timeout_commit` in genesis.
```json
{'block_gas_limit': 20000000,
 'block_gas_used': '1594395 (7.971975%)',
 'block_time_use': '5s',
 'block_txs': 66,
 'current_height': 242,
 'mempool_contract_txs': 2443,
 'mempool_normal_txs': 2489,
 'mempool_total_txs': 4932}
{'block_gas_limit': 20000000,
 'block_gas_used': '1594395 (7.971975%)',
 'block_time_use': '5s',
 'block_txs': 66,
 'current_height': 243,
 'mempool_contract_txs': 2444,
 'mempool_normal_txs': 2490,
 'mempool_total_txs': 4934}
send normal tx error:  {'code': -32000, 'message': ': mempool is full'}
send contract tx error: {'code': -32000, 'message': ': mempool is full'}
send normal tx error:  {'code': -32000, 'message': ': mempool is full'}
send contract tx error: {'code': -32000, 'message': ': mempool is full'}
{'block_gas_limit': 20000000,
 'block_gas_used': '1600710 (8.00355%)',
 'block_time_use': '6s',
 'block_txs': 66,
 'current_height': 244,
 'mempool_contract_txs': 2445,
 'mempool_normal_txs': 2492,
 'mempool_total_txs': 4937}
{'block_gas_limit': 20000000,
 'block_gas_used': '1615395 (8.076975%)',
 'block_time_use': '5s',
 'block_txs': 67,
 'current_height': 245,
 'mempool_contract_txs': 2412,
 'mempool_normal_txs': 2458,
 'mempool_total_txs': 4870}
{'block_gas_limit': 20000000,
 'block_gas_used': '1615395 (8.076975%)',
 'block_time_use': '5s',
 'block_txs': 67,
 'current_height': 246,
 'mempool_contract_txs': 2379,
 'mempool_normal_txs': 2424,
 'mempool_total_txs': 4803}
{'block_gas_limit': 20000000,
 'block_gas_used': '1594395 (7.971975%)',
 'block_time_use': '6s',
 'block_txs': 66,
 'current_height': 247,
 'mempool_contract_txs': 2346,
 'mempool_normal_txs': 2391,
 'mempool_total_txs': 4737}
```