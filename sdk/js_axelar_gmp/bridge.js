const xrpl = require('xrpl');
const ethers = require('ethers');

// Axelar Configuration
const AXELAR_GATEWAY_XRPL = "rM2ZZz9QW4i5sD6aN7i2b5EwSTr4sK7S3q";
const DESTINATION_CHAIN_NAME = "xrpl-evm-sidechain";

async function main() {
    // 1. Get command line arguments
    const args = process.argv.slice(2);
    if (args.length < 7) {
        console.error("Usage: node bridge.js <senderSecret> <xrplNodeUrl> <mptIssuanceId> <issuerAddress> <amountToBridge> <destinationEvmAddress> <evmTwinContractAddress>");
        process.exit(1);
    }
    const [
        senderSecret,
        xrplNodeUrl,
        mptIssuanceId,
        issuerAddress,
        amountToBridge,
        destinationEvmAddress,
        evmTwinContractAddress
    ] = args;
    
    // 2. Connect to the XRPL
    const client = new xrpl.Client(xrplNodeUrl);
    await client.connect();
    const senderWallet = xrpl.Wallet.fromSeed(senderSecret);

    // 3. Prepare EVM payload
    const mintInterface = new ethers.Interface(["function mint(address to, uint256 amount)"]);
    const payload = mintInterface.encodeFunctionData("mint", [destinationEvmAddress, amountToBridge]);

    // 4. Construct Axelar GMP memo
    const gmpMemo = {
        destination_chain: DESTINATION_CHAIN_NAME,
        destination_address: evmTwinContractAddress,
        payload: payload,
    };

    // 5. Construct the XRPL Payment transaction for an MPToken
    // *** DEFINITIVE FIX: Use the 'mpt_issuance_id' key as required by the xrpl.js library ***
    const paymentTx = {
        TransactionType: "Payment",
        Account: senderWallet.address,
        Destination: AXELAR_GATEWAY_XRPL,
        Amount: {
            mpt_issuance_id: mptIssuanceId,
            value: (parseInt(amountToBridge) / (10**6)).toString() // Convert back to standard units
        },
        Memos: [{
            Memo: {
                MemoType: xrpl.convertStringToHex("text/json"),
                MemoData: xrpl.convertStringToHex(JSON.stringify(gmpMemo))
            }
        }]
    };
    
    // 6. Autofill, sign, and submit
    try {
        const prepared = await client.autofill(paymentTx);
        const signed = senderWallet.sign(prepared);
        const result = await client.submitAndWait(signed.tx_blob);

        if (result.result.meta.TransactionResult === "tesSUCCESS") {
            console.log(JSON.stringify({ status: "success", result: result.result }));
        } else {
            console.error(JSON.stringify({ status: "failed", result: result.result }));
        }
    } catch (error) {
        console.error("Error during XRPL transaction submission:", error);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
}

main();