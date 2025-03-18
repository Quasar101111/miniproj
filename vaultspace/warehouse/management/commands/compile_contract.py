import json
from solcx import compile_source, install_solc
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Compiles the Warehouse Smart Contract"

    def handle(self, *args, **kwargs):
        try:
            contract_path = "contracts/warehouse_contract.sol"
            
            self.stdout.write("🔨 Starting Solidity compiler installation...")
            install_solc(version="0.8.0")
            self.stdout.write(self.style.SUCCESS("✅ Solc 0.8.0 installed"))

            with open(contract_path, "r") as file:
                contract_source = file.read()

            self.stdout.write("⚙️  Compiling smart contract...")
            compiled_sol = compile_source(contract_source, solc_version="0.8.0")
            contract_id, contract_interface = compiled_sol.popitem()

            # Save ABI
            with open("contracts/WarehouseContract_abi.json", "w") as abi_file:
                json.dump(contract_interface["abi"], abi_file, indent=4)
            
            # Save Bytecode
            with open("contracts/WarehouseContract_bytecode.txt", "w") as bytecode_file:
                bytecode_file.write(contract_interface["bin"])

            # Success output
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.SUCCESS("🎉 Smart Contract Compiled Successfully!"))
            self.stdout.write(self.style.SUCCESS(f"📄 ABI Location: contracts/WarehouseContract_abi.json"))
            self.stdout.write(self.style.SUCCESS(f"🔢 Bytecode Location: contracts/WarehouseContract_bytecode.txt"))
            self.stdout.write("="*50 + "\n")

        except Exception as e:
            self.stdout.write(self.style.ERROR("\n💥 Compilation Failed!"))
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            self.stdout.write(self.style.WARNING("⚠️  Check: \n1. Solidity file syntax \n2. Write permissions \n3. Solc version"))