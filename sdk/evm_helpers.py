import json
import os
from web3 import Web3

def deploy_erc20_twin_on_evm(
    w3: Web3,
    deployer_account: dict,
    token_name: str,
    token_symbol: str
):
    """
    Deploys a 'BridgedMPToken' contract to an EVM-compatible chain.
    """
    print(f"🔹 Preparing to deploy '{token_name}' ({token_symbol}) ERC20 twin contract to EVM chain...")

    try:
        script_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(script_dir, '..'))
        artifact_path = os.path.join(
            project_root, 
            'artifacts', 
            'contracts', 
            'BridgedMPToken.sol', 
            'BridgedMPToken.json'
        )
        print(f"   Artifact path: {artifact_path}") 

        with open(artifact_path) as f:
            artifact = json.load(f)
        
        abi = artifact['abi']
        bytecode = artifact['bytecode']

        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(deployer_account['address'])
        
        tx = contract.constructor(
            token_name,
            token_symbol,
            deployer_account['address']
        ).build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'from': deployer_account['address'],
            'nonce': nonce
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=deployer_account['private_key'])
        
        print("🔹 Submitting contract deployment transaction to EVM chain...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"✅ Success! Contract deployed.")
        return {
            "status": "success",
            "tx_hash": tx_hash.hex(),
            "contract_address": tx_receipt.contractAddress
        }
    except Exception as e:
        print(f"❌ An exception occurred during EVM deployment: {e}")
        return {"status": "exception", "error": str(e)}

def get_erc20_balance_evm(
    w3: Web3,
    contract_address: str,
    account_address: str
):
    """
    Queries the balance of an ERC20 token for a given account on an EVM chain.
    """
    print(f"🔹 Querying ERC20 balance for contract {contract_address[:10]}... on account {account_address[:10]}...")
    try:
        min_abi = [
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
        ]
        token_contract = w3.eth.contract(address=contract_address, abi=min_abi)
        balance = token_contract.functions.balanceOf(account_address).call()
        print(f"✅ Found balance: {balance}")
        return balance
    except Exception as e:
        print(f"❌ An exception occurred while querying ERC20 balance: {e}")
        return -1 