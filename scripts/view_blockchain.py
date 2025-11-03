from blockchain_helper import BlockchainManager

def main():
    bc = BlockchainManager()
    
    print("\n" + "="*60)
    print("BLOCKCHAIN DELIVERIES")
    print("="*60)
    print(f"Contract: {bc.contract.address}\n")
    
    # Show first 10 deliveries
    print("First 10 Deliveries:")
    print("-" * 60)
    for i in range(1, 11):
        delivery_id = f'D{i:04d}'
        try:
            d = bc.get_delivery(delivery_id)
            print(f"{d['id']}: {d['status']:25} | Loc: ({d['current_lat']:.2f}, {d['current_lon']:.2f})")
        except:
            print(f"{delivery_id}: Not found")
    
    print("\n... (90 more deliveries on blockchain)")
    print("\n" + "="*60)
    print("To view specific delivery, use:")
    print("  brownie console --network development")
    print("  >>> from blockchain_helper import BlockchainManager")
    print("  >>> bc = BlockchainManager()")
    print("  >>> bc.get_delivery('D0050')")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
