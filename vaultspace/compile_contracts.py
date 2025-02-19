from solcx import install_solc, compile_standard, get_installed_solc_versions, set_solc_version
import json

# Install and set Solidity compiler version (MUST match deployment setup)
if '0.8.0' not in get_installed_solc_versions():
    install_solc('0.8.0')
set_solc_version('0.8.0')

def compile_contract():
    with open("vaultspace/contracts/WarehouseRegistry.sol", "r") as f:
        source = f.read()
    
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            "WarehouseRegistry.sol": {"content": source}
        },
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        }
    })
    
    with open("vaultspace/compiled_code.json", "w") as f:
        json.dump(compiled, f)

if __name__ == "__main__":
    compile_contract()