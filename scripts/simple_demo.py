from brownie import SimpleDeliveryTracker, accounts
import csv
from datetime import datetime

def coord_to_int(coord):
    return int(float(coord) * 1_000_000)

def main():
    account = accounts[0]
    
    # Deploy contract
    contract = SimpleDeliveryTracker.deploy({'from': account})
    print(f"✓ Contract deployed at: {contract.address}")
    
    # Load first 5 deliveries from CSV
    print("\n✓ Loading deliveries from CSV...")
    with open('sample_delivery_dataset.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        for row in csv_reader:
            if count >= 5:  # Only load 5 for demo
                break
            
            timestamp = int(datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S.%f').timestamp())
            
            contract.setDelivery(
                row['Delivery_ID'],
                coord_to_int(row['Origin_Latitude']),
                coord_to_int(row['Origin_Longitude']),
                coord_to_int(row['Destination_Latitude']),
                coord_to_int(row['Destination_Longitude']),
                row['Status'],
                timestamp,
                coord_to_int(row['Current_Latitude']),
                coord_to_int(row['Current_Longitude']),
                {'from': account}
            )
            print(f"  Added {row['Delivery_ID']} - {row['Status']}")
            count += 1
    
    # Demonstrate get functions
    print("\n✓ Testing get functions:")
    delivery = contract.getDelivery('D0001')
    print(f"  Full delivery D0001: Status={delivery[5]}, Location=({delivery[7]/1e6}, {delivery[8]/1e6})")
    
    status = contract.getStatus('D0001')
    print(f"  Status only: {status}")
    
    location = contract.getLocation('D0001')
    print(f"  Location only: ({location[0]/1e6}, {location[1]/1e6})")
    
    # Demonstrate set functions
    print("\n✓ Testing set functions:")
    contract.setStatus('D0001', 'Delivered', {'from': account})
    print(f"  Updated status to: {contract.getStatus('D0001')}")
    
    contract.setLocation('D0001', coord_to_int(40.0), coord_to_int(-75.0), {'from': account})
    new_loc = contract.getLocation('D0001')
    print(f"  Updated location to: ({new_loc[0]/1e6}, {new_loc[1]/1e6})")
    
    print(f"\n✓ Demo complete! Contract address: {contract.address}")
