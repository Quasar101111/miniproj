from django.core.management.base import BaseCommand
from django.test import TestCase
from blockchain.service import BlockchainService
from web3 import Web3
import os

class BlockchainTests(TestCase):
    def test_blockchain_flow(self):
        # Test configuration
        service = BlockchainService()
       
        # 1. Test contract connection
        self.assertTrue(service.w3.is_connected())
       
        # 2. Check wallet balance
        wallet_address = os.getenv('WALLET_ADDRESS')
        balance = service.w3.eth.get_balance(wallet_address)
        min_balance = Web3.to_wei(0.01, 'ether')  # Minimum required balance
        if balance < min_balance:
            raise ValueError(
                f"Insufficient funds in wallet {wallet_address}. "
                f"Current balance: {Web3.from_wei(balance, 'ether')} ETH. "
                "Get test ETH from a Sepolia faucet."
            )
       
        # 3. Build and sign transaction
        nonce = service.w3.eth.get_transaction_count(wallet_address)
       
        # Get current gas price from network
        current_gas_price = service.w3.eth.gas_price
        if current_gas_price == 0:
            raise ValueError("Invalid gas price received from network")
        
        # Use a higher fixed gas limit instead of trying to estimate
        gas_limit = 300000  # This should be sufficient for most contract interactions
        
        # Build the transaction
        tx = service.contract.functions.addWarehouse(
            "Test Warehouse",
            "Test Location",
            1000,
            2000
        ).build_transaction({
            'from': wallet_address,
            'nonce': nonce,
            'gas': gas_limit,
            'maxFeePerGas': int(current_gas_price * 2),
            'maxPriorityFeePerGas': int(current_gas_price * 1.5),
        })
       
        # Check if the wallet has enough balance to cover the gas fees
        total_gas_cost = gas_limit * current_gas_price
        if balance < total_gas_cost:
            raise ValueError(
                f"Insufficient funds to cover gas fees. "
                f"Required: {Web3.from_wei(total_gas_cost, 'ether')} ETH, "
                f"Current balance: {Web3.from_wei(balance, 'ether')} ETH."
            )
       
        # Sign the transaction
        signed_tx = service.w3.eth.account.sign_transaction(tx, private_key=os.getenv('PRIVATE_KEY'))
       
        # Send the signed transaction
        try:
            tx_hash = service.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        except Exception as e:
            raise ValueError(f"Transaction failed: {str(e)}")
       
        # 4. Verify transaction
        receipt = service.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        self.assertEqual(receipt.status, 1)
       
        # Return the transaction hash for printing
        return tx_hash.hex()

class Command(BaseCommand):
    help = "Run blockchain tests"
   
    def handle(self, *args, **kwargs):
        try:
            tester = BlockchainTests(methodName='test_blockchain_flow')
            tx_hash = tester.test_blockchain_flow()
           
            # Print transaction information
            self.stdout.write(f"\nTransaction Hash: {tx_hash}")
            self.stdout.write(f"Etherscan URL: https://sepolia.etherscan.io/tx/{tx_hash}")
            self.stdout.write(self.style.SUCCESS("✅ Blockchain tests passed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Test failed: {str(e)}"))