import os
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc, get_installed_solc_versions, set_solc_version

# Load environment variables
load_dotenv()

# Connect to Infura (Sepolia Testnet)
infura_url = os.getenv("INFURA_URL")
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection
if web3.is_connected():
    print("Connected to Sepolia Testnet ✅")
else:
    print("Failed to connect to blockchain ❌")
    exit()

# Get wallet address and private key from .env
wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# Install and set Solidity compiler version
if '0.8.0' not in get_installed_solc_versions():
    install_solc('0.8.0')
set_solc_version('0.8.0')

# Smart contract source code (Solidity)
contract_source_code = '''
pragma solidity ^0.8.0;

contract WarehouseStorage {
    struct Warehouse {
        string name;
        string location;
        string details;
        address owner;
    }

    Warehouse[] public warehouses;
    mapping(uint => address) public warehouseToOwner;

    event WarehouseAdded(uint indexed warehouseId, string name, string location, address owner);

    function addWarehouse(string memory _name, string memory _location, string memory _details) public {
        warehouses.push(Warehouse(_name, _location, _details, msg.sender));
        uint id = warehouses.length - 1;
        warehouseToOwner[id] = msg.sender;
        emit WarehouseAdded(id, _name, _location, msg.sender);
    }

    function getWarehouse(uint _id) public view returns (string memory, string memory, string memory, address) {
        require(_id < warehouses.length, "Warehouse ID does not exist");
        Warehouse memory w = warehouses[_id];
        return (w.name, w.location, w.details, w.owner);
    }

    function getTotalWarehouses() public view returns (uint) {
        return warehouses.length;
    }
}
'''

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "WarehouseStorage.sol": {
            "content": contract_source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
        }
    }
})

# Get ABI and Bytecode from the compiled contract
abi = compiled_sol['contracts']['WarehouseStorage.sol']['WarehouseStorage']['abi']
bytecode = compiled_sol['contracts']['WarehouseStorage.sol']['WarehouseStorage']['evm']['bytecode']['object']

# Create contract instance
WarehouseStorage = web3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy the contract
def deploy_contract():
    # Get current base fee and priority fee
    latest_block = web3.eth.get_block('latest')
    base_fee = latest_block['baseFeePerGas']
    priority_fee = web3.eth.max_priority_fee
    
    # Calculate max fee with 10% buffer
    max_fee = int(base_fee * 1.1) + priority_fee
    
    # Build transaction with EIP-1559 parameters
    transaction = {
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'nonce': web3.eth.get_transaction_count(wallet_address),
        'chainId': 11155111,
        'from': wallet_address
    }

    # Estimate gas limit
    gas_estimate = WarehouseStorage.constructor().estimate_gas(transaction)
    transaction['gas'] = int(gas_estimate * 1.2)  # 20% buffer
    
    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Contract Deployment Transaction Hash: {web3.to_hex(txn_hash)}")

    # Wait for the transaction receipt
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Contract deployed at address: {txn_receipt.contractAddress}")
    return txn_receipt.contractAddress

# Deploy and get the contract address
contract_address = deploy_contract()
print(f"Contract deployed to: {contract_address}")
