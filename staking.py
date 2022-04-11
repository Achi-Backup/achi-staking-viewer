import os.path
import sqlite3
from bech32m import encode_puzzle_hash

print("ACHI Staking Viewer 1.0\n")
print("Analyzing coin database...\n")

db = os.path.expanduser("~/.achi/mainnet/db/blockchain_v1_mainnet.sqlite")
conn = sqlite3.connect(db)

dbcursor = conn.cursor()
dbcursor.execute("SELECT confirmed_index, puzzle_hash, amount from coin_record where spent = 0")
rows = dbcursor.fetchall()

sten_per_achi = 1_000_000_000
staking_value = 1_000_000.0
halving = 1142784

staking_coins = {}
total_staking_coins = 0
emission = 0.0

for row in rows:
    block = row[0]
    sten = int.from_bytes(row[2], 'big')
    ach = sten / sten_per_achi
    emission += ach

    if block < halving and ach >= staking_value:
        ph = bytes.fromhex(row[1])
        address = encode_puzzle_hash(ph, 'ach')

        if address.startswith("ach1stake"):
            if address not in staking_coins:
                staking_coins[address] = {
                    "coins": 0,
                    "amount": 0.0
                }

            staking_coins[address]["coins"] += 1
            staking_coins[address]["amount"] += ach
            total_staking_coins += 1

columns = ["Staking address", "Coins", "Percent", "Staked", "Non staked"]
print(f"{columns[0]:62} {columns[1]:>5} {columns[2]:>8} {columns[3]:>18} {columns[4]:>18}")
print("-" * 115)

for address in staking_coins:
    coins = staking_coins[address]['coins']
    amount = coins * staking_value
    percent = coins / total_staking_coins * 100.0
    total_amount = staking_coins[address]['amount']
    print(f"{address} {coins:5} {percent:7.2f}% {amount:>14,.2f} ach {total_amount - amount:>14,.2f} ach")

print("-" * 115)
print(f"Total emission: {emission:,.2f} ach")
print(f"Total staked: {total_staking_coins * staking_value:,.2f} ach")
print(f"Emission staked: {total_staking_coins * staking_value / emission:,.2f}%")
