from brownie import SimpleDeliveryTracker, accounts, network
import csv
from datetime import datetime

def coord_to_int(coord):
    return int(float(coord) * 1_000_000)

def main():
    # Connect to running Ganache
    if not network.is_connected():
        network.connect('development')
    
    # Load contract address
    with open('contract_address.txt', 'r') as f:
        contract_address = f.read().strip()
    
    contract = SimpleDeliveryTracker.at(contract_address)
    account = accounts[0]
    
    print(f"✓ Connected to contract: {contract_address}")
    print("\n✓ Loading ALL deliveries from CSV...")
    
    # Load all deliveries from CSV
    with open('sample_delivery_dataset.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        
        for row in csv_reader:
            try:
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
                
                count += 1
                print(f"  [{count}] Added {row['Delivery_ID']} - {row['Status']}")
                
            except Exception as e:
                print(f"  Error adding {row['Delivery_ID']}: {e}")
    
    print(f"\n✓ Complete! Loaded {count} deliveries to blockchain")
    print(f"✓ Contract address: {contract_address}")
