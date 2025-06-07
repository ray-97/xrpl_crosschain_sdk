from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet  # Keep this import
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Load configuration from .env file
XRPL_TESTNET_URL = os.getenv("XRPL_TESTNET_URL")
XRPL_ACCOUNT_SECRET = os.getenv("XRPL_ACCOUNT_SECRET")

if not XRPL_TESTNET_URL or not XRPL_ACCOUNT_SECRET:
    print("Error: Make sure XRPL_TESTNET_URL and XRPL_ACCOUNT_SECRET are set in your .env file.")
else:
    try:
        # 2. Initialize the Wallet object from the secret using the .from_seed() method
        test_wallet = Wallet.from_seed(XRPL_ACCOUNT_SECRET)

        # 3. Initialize the client to connect to the testnet
        client = JsonRpcClient(XRPL_TESTNET_URL)

        print(f"✅ Successfully created a wallet.")
        print(f"Wallet address: {test_wallet.classic_address}")
        print(f"Connected to XRPL Testnet at: {XRPL_TESTNET_URL}")
        print("---")
        print("This script is a success! You are ready to interact with the XRPL.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check that your XRPL_ACCOUNT_SECRET in the .env file is correct.")