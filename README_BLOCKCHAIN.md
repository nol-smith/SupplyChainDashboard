# Supply Chain Blockchain Integration

## Smart Contract
**File:** `contracts/SimpleDeliveryTracker.sol`

### Features
- Stores all delivery data (ID, origin, destination, status, timestamp, current location)
- **setDelivery()** - Add/update complete delivery with all fields
- **getDelivery()** - Retrieve complete delivery information
- **setStatus()** - Update delivery status only
- **getStatus()** - Get delivery status only
- **setLocation()** - Update current location only
- **getLocation()** - Get current location only

## Quick Demo

### Run the demo:
```bash
brownie run scripts/simple_demo.py
```

This will:
1. Deploy the smart contract
2. Load 5 sample deliveries from CSV to blockchain
3. Demonstrate all get/set functions
4. Show updated status and location

### For Your Dashboard
Your Python dashboard can connect to the deployed contract and call:
- `contract.getDelivery('D0001')` - Get all delivery data
- `contract.getStatus('D0001')` - Get just the status
- `contract.setStatus('D0001', 'Delivered')` - Update status
- `contract.setLocation('D0001', lat, lon)` - Update location

## Contract Address
After running the demo, save the contract address shown in the output to connect your dashboard.
