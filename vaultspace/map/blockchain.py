# from web3 import Web3
# import os, json
# from dotenv import load_dotenv
# from pathlib import Path

# # Load environment variables
# load_dotenv()

# # Connect to Infura (Sepolia Testnet)
# infura_url = os.getenv("INFURA_URL")
# web3 = Web3(Web3.HTTPProvider(infura_url))

# # Keep wallet address and private key
# wallet_address = os.getenv("WALLET_ADDRESS")
# private_key = os.getenv("PRIVATE_KEY")

# def get_contract():
#     # Get the project root directory
#     BASE_DIR = Path(__file__).resolve().parent.parent
    
#     # Construct full path to compiled code
#     compiled_path = BASE_DIR / "compiled_code.json"
    
#     with open(compiled_path, "r") as f:
#         compiled_data = json.load(f)
    
#     return web3.eth.contract(
#         address=os.getenv("CONTRACT_ADDRESS"),
#         abi=compiled_data['contracts']['WarehouseRegistry.sol']['WarehouseRegistry']['abi']
#     )

# def add_warehouse(data):
#     contract = get_contract()
#     txn = contract.functions.addWarehouse(
#         data['name'],
#         data['location'],
#         data['capacity'],
#         data['facilities']
#     ).build_transaction({
#         'from': os.getenv("WALLET_ADDRESS"),
#         'nonce': contract.w3.eth.get_transaction_count(os.getenv("WALLET_ADDRESS"))
#     })
    
#     signed = contract.w3.eth.account.sign_transaction(txn, os.getenv("PRIVATE_KEY"))
#     return contract.w3.eth.send_raw_transaction(signed.raw_transaction)

# # Fix example usage to match 4 parameters
# add_warehouse({
#     'name': "Warehouse 1",
#     'location': "Location 1",
#     'capacity': 1000,
#     'facilities': "Cold storage, Security system"
# })
