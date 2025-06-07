import sys
import os
import json
import binascii
import time
# This adds the project root to the Python path, so we can find the 'sdk' module.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from web3 import Web3
# Import our SDK functions
from sdk.xrpl_helpers import create_mptoken_on_xrpl
from sdk.evm_helpers import deploy_erc20_twin_on_evm, get_erc20_balance_evm
from sdk.mock_axelar_helpers import mock_bridge_and_mint

def main():
    """
    A demo script to showcase the SDK's functionality.
    This version shows the simplified flow: create, deploy, and MOCK the bridge.
    """
    load_dotenv()
    print("--- Loading configuration ---")

    # XRPL Client Setup
    xrpl_url = os.getenv("XRPL_TESTNET_URL")
    issuer_secret = os.getenv("XRPL_ACCOUNT_SECRET")

    if not xrpl_url or not issuer_secret:
        raise Exception("XRPL_TESTNET_URL and XRPL_ACCOUNT_SECRET must be set in .env")
    
    xrpl_client = JsonRpcClient(xrpl_url)
    issuer_wallet = Wallet.from_seed(issuer_secret)
    
    print(f"Connected to XRPL: {xrpl_url}")
    print(f"Issuer Wallet Address: {issuer_wallet.classic_address}")

    # EVM Sidechain Setup
    evm_rpc_url = os.getenv("EVM_SIDECHAIN_RPC_URL")
    evm_private_key = os.getenv("EVM_PRIVATE_KEY")
    
    if not evm_rpc_url or not evm_private_key:
        raise Exception("EVM_SIDECHAIN_RPC_URL and EVM_PRIVATE_KEY must be set in .env")
        
    w3 = Web3(Web3.HTTPProvider(evm_rpc_url))
    
    try:
        evm_account = w3.eth.account.from_key(evm_private_key)
    except binascii.Error:
        print("\n❌ FATAL ERROR: The EVM_PRIVATE_KEY is not a valid hexadecimal string.")
        return

    deployer_account_info = {
        "address": evm_account.address,
        "private_key": evm_private_key
    }
    
    print(f"\nConnected to EVM Sidechain: {evm_rpc_url}")
    print(f"Deployer EVM Address: {deployer_account_info['address']}")
    
    # --- Step 1: Create the MPToken on XRPL ---
    print("\n--- Step 1: Creating a new MPToken on XRPL ---")
    token_name = "Hackathon Demo Token"
    token_symbol = "HDT"
    
    token_creation_result = create_mptoken_on_xrpl(
        client=xrpl_client, issuer_wallet=issuer_wallet, token_name=token_name,
        token_symbol=token_symbol, decimals=6, max_supply="1000000000000", transfer_fee=500
    )
    
    if token_creation_result.get("status") != "success":
        print("\n❌ MPToken creation failed. Aborting demo.")
        return

    new_issuance_id = token_creation_result["issuance_id"]
    print(f"\n🚀 MPToken created successfully! Issuance ID: {new_issuance_id}")
    
    # --- Step 2: Deploy the ERC20 Twin Contract ---
    print("\n--- Step 2: Deploying the ERC20 Twin contract to the EVM Sidechain ---")
    
    deployment_result = deploy_erc20_twin_on_evm(
        w3=w3, deployer_account=deployer_account_info,
        token_name=token_name, token_symbol=token_symbol
    )
    
    if deployment_result["status"] != "success":
        print("\n❌ ERC20 deployment failed. Aborting demo.")
        return

    twin_contract_address = deployment_result["contract_address"]
    print(f"\n🚀 ERC20 Twin contract deployed successfully! Contract Address: {twin_contract_address}")
    
    # --- Step 3: Verify initial EVM balance is 0 ---
    print("\n--- Step 3: Verifying initial ERC20 balance on EVM Sidechain ---")
    initial_erc20_balance = get_erc20_balance_evm(
        w3=w3,
        contract_address=twin_contract_address,
        account_address=deployer_account_info["address"]
    )
    print(f"\nDeployer's initial balance of the ERC20 token: {initial_erc20_balance} {token_symbol}")

    # --- Step 4: MOCK the bridge call and mint tokens on EVM ---
    print("\n--- Step 4: Simulating the bridge of 123 tokens from XRPL to EVM ---")
    
    bridge_amount_smallest_units = 123000000 # 123 tokens with 6 decimals
    
    mock_bridge_result = mock_bridge_and_mint(
        w3=w3,
        deployer_account=deployer_account_info,
        twin_contract_address=twin_contract_address,
        destination_address=deployer_account_info["address"],
        amount_to_mint=bridge_amount_smallest_units
    )

    if mock_bridge_result.get("status") != "success":
        print("\n❌ Mock bridging transaction failed. Aborting demo.")
        return

    print("\n🚀 Mock bridge simulation complete.")
    
    # --- Step 5: Verify the final balance on the EVM Sidechain ---
    print("\n--- Step 5: Verifying the final ERC20 balance on EVM Sidechain ---")
    final_erc20_balance = get_erc20_balance_evm(
        w3=w3,
        contract_address=twin_contract_address,
        account_address=deployer_account_info["address"]
    )
    print(f"\nDeployer's final balance of the ERC20 token: {final_erc20_balance} (smallest units)")
    
    if final_erc20_balance == bridge_amount_smallest_units:
        print("\n🎉🎉🎉 SUCCESS! The final balance on the EVM sidechain is correct. End-to-end flow demonstrated! �🎉🎉")
    else:
        print("\n🤔 The final balance is not what was expected. Please check the logs.")


if __name__ == "__main__":
    main()