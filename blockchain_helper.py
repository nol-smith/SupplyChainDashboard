from brownie import SimpleDeliveryTracker, accounts, network
import time
import os

class BlockchainManager:
    def __init__(self):
        # Connect to persistent Ganache
        if not network.is_connected():
            network.connect('development')
        
        # Load or deploy contract
        if os.path.exists('contract_address.txt'):
            with open('contract_address.txt', 'r') as f:
                contract_address = f.read().strip()
            self.contract = SimpleDeliveryTracker.at(contract_address)
        else:
            # Deploy new contract if address file doesn't exist
            self.contract = SimpleDeliveryTracker.deploy({'from': accounts[0]})
            with open('contract_address.txt', 'w') as f:
                f.write(self.contract.address)
        
        self.account = accounts[0]
    
    def add_delivery(self, delivery_id, origin_lat, origin_lon, dest_lat, dest_lon, status, current_lat, current_lon):
        """Add a new delivery to blockchain"""
        tx = self.contract.setDelivery(
            delivery_id,
            int(origin_lat * 1_000_000),
            int(origin_lon * 1_000_000),
            int(dest_lat * 1_000_000),
            int(dest_lon * 1_000_000),
            status,
            int(time.time()),
            int(current_lat * 1_000_000),
            int(current_lon * 1_000_000),
            {'from': self.account}
        )
        return tx
    
    def get_delivery(self, delivery_id):
        """Get delivery from blockchain"""
        delivery = self.contract.getDelivery(delivery_id)
        return {
            'id': delivery[0],
            'origin_lat': delivery[1] / 1_000_000,
            'origin_lon': delivery[2] / 1_000_000,
            'dest_lat': delivery[3] / 1_000_000,
            'dest_lon': delivery[4] / 1_000_000,
            'status': delivery[5],
            'timestamp': delivery[6],
            'current_lat': delivery[7] / 1_000_000,
            'current_lon': delivery[8] / 1_000_000
        }
    
    def update_status(self, delivery_id, new_status):
        """Update delivery status"""
        tx = self.contract.setStatus(delivery_id, new_status, {'from': self.account})
        return tx
    
    def update_location(self, delivery_id, lat, lon):
        """Update delivery location"""
        tx = self.contract.setLocation(
            delivery_id,
            int(lat * 1_000_000),
            int(lon * 1_000_000),
            {'from': self.account}
        )
        return tx
    
    def get_status(self, delivery_id):
        """Get delivery status only"""
        return self.contract.getStatus(delivery_id)
    
    def get_location(self, delivery_id):
        """Get delivery location only"""
        location = self.contract.getLocation(delivery_id)
        return {
            'lat': location[0] / 1_000_000,
            'lon': location[1] / 1_000_000
        }
