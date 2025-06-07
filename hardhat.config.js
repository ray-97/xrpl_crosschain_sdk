require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.28", // Or whatever version you have
  paths: {
    sources: "./contracts", // Add this line to specify your contracts folder
  },
};