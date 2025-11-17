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
        # Dallas to Denver - In Transit
        {'id': 'D0004', 'origin': (32.7767, -96.7970), 'dest': (39.7392, -104.9903), 
         'current': (35.4676, -97.5164), 'status': 'In Transit', 'days': 3},
        # Atlanta to Phoenix - Preparing
        {'id': 'D0005', 'origin': (33.7490, -84.3880), 'dest': (33.4484, -112.0740), 
         'current': (33.7490, -84.3880), 'status': 'Preparing for Shipment', 'days': 4},
        # Portland to Houston - In Transit
        {'id': 'D0006', 'origin': (45.5152, -122.6784), 'dest': (29.7604, -95.3698), 
         'current': (37.7749, -122.4194), 'status': 'In Transit', 'days': 2},
        # San Diego to Philadelphia - Delivered
        {'id': 'D0007', 'origin': (32.7157, -117.1611), 'dest': (39.9526, -75.1652), 
         'current': (39.9526, -75.1652), 'status': 'Delivered', 'days': 0},
        # Minneapolis to Nashville - In Transit
        {'id': 'D0008', 'origin': (44.9778, -93.2650), 'dest': (36.1627, -86.7816), 
         'current': (41.5868, -93.6250), 'status': 'In Transit', 'days': 1},
        # Las Vegas to Detroit - Delayed
        {'id': 'D0009', 'origin': (36.1699, -115.1398), 'dest': (42.3314, -83.0458), 
         'current': (39.7392, -104.9903), 'status': 'Delayed', 'days': -2},
        # San Francisco to Orlando - Preparing
        {'id': 'D0010', 'origin': (37.7749, -122.4194), 'dest': (28.5383, -81.3792), 
         'current': (37.7749, -122.4194), 'status': 'Preparing for Shipment', 'days': 5}
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
