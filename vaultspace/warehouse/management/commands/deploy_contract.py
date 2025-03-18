import os
import json
from web3 import Web3
from django.core.management.base import BaseCommand
import time
from solcx import compile_source, install_solc, get_installed_solc_versions, set_solc_version

class Command(BaseCommand):
    help = "Deploys contract to Ethereum network"

    def handle(self, *args, **kwargs):
        try:
            # Check and install solc version first
            SOLC_VERSION = '0.8.0'
            self.stdout.write(f"⏳ Checking solc version {SOLC_VERSION}...")
            
            if SOLC_VERSION not in [str(v) for v in get_installed_solc_versions()]:
                self.stdout.write(f"🔧 Installing solc version {SOLC_VERSION}...")
                install_solc(SOLC_VERSION)
            
            set_solc_version(SOLC_VERSION)
            self.stdout.write(f"✅ Using solc version {SOLC_VERSION}")

            # Validate environment variables FIRST
            required_vars = ['NETWORK', 'INFURA_PROJECT_ID', 'PRIVATE_KEY', 'WALLET_ADDRESS']
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Missing environment variables: {', '.join(missing)}")

            # Now safely access variables
            network = os.getenv('NETWORK')  # Guaranteed to exist after validation
            infura_url = f"https://{network}.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
            
            self.stdout.write(f"⏳ Connecting to {network.capitalize()} network...")

            # Load environment
            priv_key = os.getenv('PRIVATE_KEY')
            wallet = os.getenv('WALLET_ADDRESS')

            # Initialize Web3 with timeout
            w3 = Web3(Web3.HTTPProvider(infura_url, request_kwargs={'timeout': 60}))
            
            if not w3.is_connected():
                raise ConnectionError(f"🔴 Failed to connect to {infura_url.split('/')[2]} (check network/credentials)")

            # Check wallet balance first
            balance = w3.eth.get_balance(wallet)
            min_balance = Web3.to_wei(0.01, 'ether')
            
            if balance < min_balance:
                raise ValueError(
                    f"Insufficient funds in wallet {wallet}. "
                    f"Current balance: {Web3.from_wei(balance, 'ether')} ETH. "
                    "Get test ETH from a Sepolia faucet."
                )

            # Load contract
            with open('contracts/Warehouse_contract.sol', 'r') as file:
                contract_source = file.read()

            self.stdout.write("📄 Compiling contract...")
            
            # Get contract bytecode and abi
            compiled = compile_source(
                contract_source,
                output_values=['abi', 'bin'],
                solc_version=SOLC_VERSION
            )
            contract_id, contract_interface = compiled.popitem()
            bytecode = contract_interface['bin']
            abi = contract_interface['abi']

            # Save ABI
            with open('contracts/WarehouseContract_abi.json', 'w') as f:
                json.dump(abi, f)

            # Get current gas price and nonce
            current_gas_price = w3.eth.gas_price
            if current_gas_price == 0:
                raise ValueError("Invalid gas price received from network")
            
            nonce = w3.eth.get_transaction_count(wallet)
            
            # Use fixed gas limit
            gas_limit = 300000

            # Build transaction
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            tx = contract.constructor().build_transaction({
                'chainId': 11155111,  # Sepolia
                'from': wallet,
                'nonce': nonce,
                'gas': gas_limit,
                'maxFeePerGas': int(current_gas_price * 2),
                'maxPriorityFeePerGas': int(current_gas_price * 1.5),
            })

            # Check if we have enough balance for gas
            total_gas_cost = gas_limit * current_gas_price
            if balance < total_gas_cost:
                raise ValueError(
                    f"Insufficient funds to cover gas fees. "
                    f"Required: {Web3.from_wei(total_gas_cost, 'ether')} ETH, "
                    f"Current balance: {Web3.from_wei(balance, 'ether')} ETH."
                )

            # Sign and deploy
            self.stdout.write("🚀 Deploying contract...")
            signed_tx = w3.eth.account.sign_transaction(tx, os.getenv('PRIVATE_KEY'))
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for deployment with timeout
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            contract_address = receipt.contractAddress

            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Contract deployed successfully!"
                f"\nNetwork: {network.capitalize()}"
                f"\nContract Address: {contract_address}"
                f"\nTransaction Hash: {tx_hash.hex()}"
                f"\nEtherscan URL: https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
            ))

            # Update .env file with contract address
            with open('.env', 'r') as f:
                env_file = f.read()
            
            if 'CONTRACT_ADDRESS' in env_file:
                env_file = env_file.replace(
                    f"CONTRACT_ADDRESS={os.getenv('CONTRACT_ADDRESS')}",
                    f"CONTRACT_ADDRESS={contract_address}"
                )
            else:
                env_file += f"\nCONTRACT_ADDRESS={contract_address}"
            
            with open('.env', 'w') as f:
                f.write(env_file)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Deployment failed: {str(e)}"))
            return