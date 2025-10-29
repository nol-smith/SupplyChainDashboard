# How to Use the Blockchain Supply Chain Dashboard

## Every Time You Want to Work on This Project

### Step 1: Start Ganache (Blockchain Server)

Open Terminal and run:
```bash
cd /Users/nolan/Desktop/supply-chain/SupplyChainDashboard
conda activate python-julia
./start_ganache.sh
```

**Keep this terminal open!** You'll see:
```
ganache v7.x.x
Available Accounts
==================
(0) 0x66aB6D9362d4F35596279692F0251Db635165871 (1000 ETH)
...

Listening on 127.0.0.1:8545
```

### Step 2: Work on Your Dashboard

Open a **NEW** terminal (Cmd+T or Cmd+N) and run:
```bash
cd /Users/nolan/Desktop/supply-chain/SupplyChainDashboard
conda activate base
# Run your dashboard here (when you create it)
```

### Step 3: When Done

- Close Terminal 2 (dashboard)
- Press Ctrl+C in Terminal 1 to stop Ganache
- All data is saved in `ganache_db/` folder

---

## Testing Blockchain Functions

If you want to test blockchain functions manually:

```bash
cd /Users/nolan/Desktop/supply-chain/SupplyChainDashboard
conda activate base
brownie console --network development
```

Then in the console:
```python
from blockchain_helper import BlockchainManager
bc = BlockchainManager()

# Get a delivery
bc.get_delivery('D0001')

# Add new delivery
bc.add_delivery('D9999', 40.5, -74.5, 42.0, -73.0, 'In Transit', 41.0, -74.0)

# Update status
bc.update_status('D9999', 'Delivered')

# Get status
bc.get_status('D9999')

# Update location
bc.update_location('D9999', 41.5, -73.5)

# Get location
bc.get_location('D9999')
```

---

## Important Info

**Contract Address:** `0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87`

**Blockchain Data Location:** `ganache_db/` folder (don't delete!)

**Available Functions:**
- `bc.add_delivery(id, origin_lat, origin_lon, dest_lat, dest_lon, status, current_lat, current_lon)`
- `bc.get_delivery(id)` - Returns dict with all delivery info
- `bc.update_status(id, new_status)`
- `bc.get_status(id)`
- `bc.update_location(id, lat, lon)`
- `bc.get_location(id)`

---

## Troubleshooting

**"Connection refused" error:**
- Make sure Ganache is running in Terminal 1
- Check that you see "Listening on 127.0.0.1:8545"

**"Contract not found" error:**
- Check that `contract_address.txt` has the correct address
- Make sure you deployed the contract (already done)

**Need to redeploy everything:**
```bash
# Delete blockchain data
rm -rf ganache_db/

# Start fresh Ganache
./start_ganache.sh

# In new terminal, redeploy
brownie run scripts/simple_demo.py --network development

# Update contract_address.txt with new address
```
