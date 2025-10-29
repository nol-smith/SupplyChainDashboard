#!/bin/bash
# Start persistent Ganache blockchain
ganache --port 8545 --wallet.mnemonic "brownie" --database.dbPath ./ganache_db
