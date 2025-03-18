import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(
            f"https://{os.getenv('NETWORK')}.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
        ))
        self.contract = self.w3.eth.contract(
            address=os.getenv('CONTRACT_ADDRESS'),
            abi=self._load_abi()
        )
    
    def _load_abi(self):
        with open("contracts/WarehouseContract_abi.json") as f:
            return json.load(f)
    
    def get_tx_params(self):
        return {
            'chainId': 11155111,
            'gas': 2000000,
            'gasPrice': self.w3.to_wei('20', 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(os.getenv('WALLET_ADDRESS')),
        }