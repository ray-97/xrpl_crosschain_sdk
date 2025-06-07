from web3 import Web3
from web3.exceptions import Web3Exception
from dotenv import load_dotenv
import os

load_dotenv()

EVM_RPC_URL = os.getenv("EVM_SIDECHAIN_RPC_URL")

if not EVM_RPC_URL:
    print("❌ Error: EVM_SIDECHAIN_RPC_URL not found in your .env file.")
else:
    print(f"Attempting to connect to: {EVM_RPC_URL}")
    try:
        w3 = Web3(Web3.HTTPProvider(EVM_RPC_URL))

        # is_connected() is deprecated, use get_block('latest') in a try/except
        # to confirm a working connection.
        latest_block = w3.eth.get_block('latest')
        
        print(f"✅ Success! Connected to EVM Sidechain.")
        print(f"Chain ID: {w3.eth.chain_id}")
        print(f"Latest block number: {latest_block.number}")

    except Web3Exception as e:
        print(f"❌ Web3 Connection Error: {e}")
        print("   Please check the RPC URL in your .env file and ensure you have an internet connection.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        print("   This could be a network issue, a problem with the RPC endpoint, or a typo in the URL.")