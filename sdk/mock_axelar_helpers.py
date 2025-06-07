from web3 import Web3

def mock_bridge_and_mint(
    w3: Web3,
    deployer_account: dict,
    twin_contract_address: str,
    destination_address: str,
    amount_to_mint: int
):
    """
    Mocks the Axelar bridge by directly calling the mint function on the ERC20 contract.
    This simulates the tokens arriving from the XRPL.
    """
    print("🔹 Simulating Axelar bridge: Directly minting tokens on EVM sidechain...")
    
    try:
        # Load just the mint function ABI
        mint_abi = [{
            "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
            "name": "mint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]

        contract = w3.eth.contract(address=twin_contract_address, abi=mint_abi)
        nonce = w3.eth.get_transaction_count(deployer_account['address'])

        # Build the mint transaction
        tx = contract.functions.mint(
            destination_address,
            amount_to_mint
        ).build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'from': deployer_account['address'],
            'nonce': nonce
        })

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=deployer_account['private_key'])
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"✅ Mock bridge successful. Minted {amount_to_mint} tokens to {destination_address[:10]}...")
        return {"status": "success", "tx_hash": tx_hash.hex()}

    except Exception as e:
        print(f"❌ An exception occurred during mock bridge minting: {e}")
        return {"status": "exception", "error": str(e)}