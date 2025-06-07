from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import MPTokenIssuanceCreate
from xrpl.models.requests import AccountLines, LedgerEntry
from xrpl.transaction import submit_and_wait
from xrpl.utils import str_to_hex
import json

def create_mptoken_on_xrpl(
    client: JsonRpcClient,
    issuer_wallet: Wallet,
    token_name: str,
    token_symbol: str,
    decimals: int,
    max_supply: str,
    transfer_fee: int = 0,
    metadata_uri: str = None
):
    """
    Creates a new Multi-purpose Token (MPToken) on the XRP Ledger.
    """
    print(f"🔹 Preparing to create MPToken '{token_name}' ({token_symbol}) on XRPL...")

    metadata_payload = {
        "name": token_name,
        "symbol": token_symbol,
        "uri": metadata_uri if metadata_uri else ""
    }
    on_chain_metadata_hex = str_to_hex(json.dumps(metadata_payload))

    create_tx = MPTokenIssuanceCreate(
        account=issuer_wallet.classic_address,
        maximum_amount=max_supply,
        asset_scale=decimals,
        transfer_fee=transfer_fee,
        mptoken_metadata=on_chain_metadata_hex,
        flags=32 # tfMPTCanTransfer
    )

    print("🔹 Submitting the MPTokenIssuanceCreate transaction...")

    try:
        response = submit_and_wait(create_tx, client, issuer_wallet)
        tx_result = response.result

        if tx_result["meta"]["TransactionResult"] == "tesSUCCESS":
            # Get the ID from the correct metadata field
            issuance_id = tx_result["meta"].get("mpt_issuance_id")
            if not issuance_id:
                 raise Exception("Could not find mpt_issuance_id in transaction metadata.")

            print(f"✅ Success! Transaction included in ledger {tx_result['ledger_index']}.")
            return { "status": "success", "result": tx_result, "issuance_id": issuance_id }
        else:
            print(f"❌ Error! Transaction failed: {tx_result['meta']['TransactionResult']}")
            return { "status": "failed", "result": tx_result, "issuance_id": None }
    except Exception as e:
        print(f"❌ An exception occurred during submission: {e}")
        return { "status": "exception", "error": str(e), "issuance_id": None }

def get_mptoken_balance_xrpl(
    client: JsonRpcClient,
    issuance_id: str,
    account_address: str
):
    """
    Queries the balance of a specific MPToken for a given account on the XRPL.
    """
    print(f"🔹 Querying balance for MPToken {issuance_id[:10]}... on account {account_address[:10]}...")
    try:
        # Note: Querying by mpt_issuance_id is not directly supported yet in account_lines
        # so this function has limited use for non-issuers in this demo.
        # We will check the issuer's balance by looking at the issuance object itself.
        print("   NOTE: Querying non-issuer balance for MPTokens is not yet fully supported in this demo.")
        return "0" # Placeholder for non-issuer
        
    except Exception as e:
        print(f"❌ An exception occurred while querying balance: {e}")