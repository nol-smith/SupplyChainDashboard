from brownie import SimpleDeliveryTracker, accounts
import time
import random

def coord_to_int(coord):
    return int(float(coord) * 1_000_000)

def main():
    account = accounts[0]
    
    # Deploy contract
    contract = SimpleDeliveryTracker.deploy({'from': account})
    print(f"✓ Contract deployed at: {contract.address}")
    
    # Save contract address
    with open('contract_address.txt', 'w') as f:
        f.write(contract.address)
    
    # Create 5 realistic test deliveries
    print("\n✓ Loading test deliveries...")
    current_time = int(time.time())
    
    deliveries = [
        # NYC to LA - In Transit
        {'id': 'D0001', 'origin': (40.7128, -74.0060), 'dest': (34.0522, -118.2437), 
         'current': (39.7392, -104.9903), 'status': 'In Transit', 'days': 2},
        # Chicago to Miami - Delivered
        {'id': 'D0002', 'origin': (41.8781, -87.6298), 'dest': (25.7617, -80.1918), 
         'current': (25.7617, -80.1918), 'status': 'Delivered', 'days': 1},
        # Seattle to Boston - Delayed
        {'id': 'D0003', 'origin': (47.6062, -122.3321), 'dest': (42.3601, -71.0589), 
         'current': (41.2565, -95.9345), 'status': 'Delayed', 'days': -1},
        # Dallas to Denver - On Track
        {'id': 'D0004', 'origin': (32.7767, -96.7970), 'dest': (39.7392, -104.9903), 
         'current': (35.4676, -97.5164), 'status': 'In Transit', 'days': 3},
        # Atlanta to Phoenix - Preparing
        {'id': 'D0005', 'origin': (33.7490, -84.3880), 'dest': (33.4484, -112.0740), 
         'current': (33.7490, -84.3880), 'status': 'Preparing for Shipment', 'days': 4}
    ]
    
    for d in deliveries:
        expected_delivery = current_time + d['days'] * 24 * 60 * 60
        
        contract.setDelivery(
            d['id'],
            coord_to_int(d['origin'][0]),
            coord_to_int(d['origin'][1]),
            coord_to_int(d['dest'][0]),
            coord_to_int(d['dest'][1]),
            d['status'],
            current_time,
            coord_to_int(d['current'][0]),
            coord_to_int(d['current'][1]),
            expected_delivery,
            {'from': account}
        )
        print(f"  Added {d['id']} - {d['status']}")
    
    print(f"\n✓ Demo complete! Contract address: {contract.address}")
