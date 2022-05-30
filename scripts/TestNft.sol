//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

error MintZeroQuantity();

contract NFT721 is ERC721URIStorage {
    //auto-increment field for each token
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIds;

    mapping(address => uint256[]) private nftListByAddress;

    event Mint(address _minter, string _tokenURI);
    event BatchMint(address _minter, string _tokenURI, uint64 _quantity);
    event MintAndSetApproval(address _minter, string _tokenURI);

    constructor() ERC721("CRONOS NFT FAUCET TOKENS", "CNFT") {}

    /// @notice mint a new token
    /// @param tokenURI : token URI
    function mintToken(string memory tokenURI) external returns (uint256) {
        //set a new token id for the token to be minted
        _tokenIds.increment();
        uint256 newItemId = _tokenIds.current();

        _mint(msg.sender, newItemId); //mint the token
        _setTokenURI(newItemId, tokenURI); //generate the URI
        nftListByAddress[msg.sender].push(newItemId);

        emit Mint(msg.sender, tokenURI);

        //return token ID
        return newItemId;
    }

    /// @notice mint a new token and send to desired address
    /// @param tokenURI : token URI
    /// @param to : address
    function mintTokenTo(string memory tokenURI, address to)
        external
        returns (uint256)
    {
        //set a new token id for the token to be minted
        _tokenIds.increment();
        uint256 newItemId = _tokenIds.current();

        _mint(msg.sender, newItemId); //mint the token
        _setTokenURI(newItemId, tokenURI); //generate the URI
        // nftListByAddress[to].push(newItemId); //push to nftListByAddress list

        safeTransferFrom(msg.sender, to, newItemId);

        emit Mint(msg.sender, tokenURI);

        //return token ID
        return newItemId;
    }

    /// @notice batch mint token
    /// @param tokenURI : token URI
    function batchMintToken(string memory tokenURI, uint64 quantity) external {
        if (quantity == 0) revert MintZeroQuantity();

        for (uint64 num = 0; num < quantity; num++) {
            _tokenIds.increment();
            uint256 newItemId = _tokenIds.current();

            _mint(msg.sender, newItemId); //mint the token
            _setTokenURI(newItemId, tokenURI); //generate the URI
            nftListByAddress[msg.sender].push(newItemId);
        }

        emit BatchMint(msg.sender, tokenURI, quantity);
    }

    /// @notice fetch all tokens by address
    /// @param _address : token owner address
    function fetchAllTokens(address _address)
        external
        view
        returns (uint256[] memory)
    {
        return nftListByAddress[_address];
    }

    function removeTokenId(address tokenOwner, uint256 tokenId) private {
        if (nftListByAddress[tokenOwner].length > 0) {
            for (
                uint256 i = 0;
                i < nftListByAddress[tokenOwner].length - 1;
                i++
            ) {
                if (nftListByAddress[tokenOwner][i] == tokenId) {
                    nftListByAddress[tokenOwner][i] = nftListByAddress[
                        tokenOwner
                    ][nftListByAddress[tokenOwner].length - 1];
                    nftListByAddress[tokenOwner].pop(); // delete the last item
                    break;
                }
            }
        }
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual override(ERC721) {
        super._beforeTokenTransfer(from, to, tokenId);

        if (from != address(0)) {
            // remove the tokenId from the nftListByAddress list whenever transferred
            removeTokenId(from, tokenId);

            // push the tokenId to the token owner whenever transferred
            nftListByAddress[to].push(tokenId);
        }
    }
}
