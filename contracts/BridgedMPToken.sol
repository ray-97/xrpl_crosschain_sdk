// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BridgedMPToken
 * @dev This ERC20 contract represents an MPToken from the XRPL, bridged to the EVM sidechain.
 * - Minting is restricted to the owner (the bridge contract).
 * - Burning is available to any holder to initiate a bridge-back transaction.
 */
contract BridgedMPToken is ERC20, ERC20Burnable, Ownable {
    constructor(
        string memory name,
        string memory symbol,
        address initialOwner
    ) ERC20(name, symbol) Ownable(initialOwner) {
        // The contract is created with an initial owner.
    }

    /**
     * @dev Creates `amount` tokens for `to`, only callable by the owner.
     * This function is used by the bridge to issue tokens when they are bridged from XRPL.
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}