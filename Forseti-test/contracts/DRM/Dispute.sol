pragma solidity ^0.4.18;

import "../dependencies/Ownable.sol";
import "../Pools/Pool.sol";
import "../dependencies/SafeMath.sol";

contract DRMInterface {

  function closeDispute() public {
  }

}

contract Dispute  {
  using SafeMath for uint;

  address  public disputeCreator;
  address  public pool;
  address DRMAddress;
  bytes32  public argumentsHash;
  string public result;

  bool disputeResolved;
  bool public votesProvided;

  uint256 public blockForSeed;
  uint public arbitratorsNumber;
  uint256 public budgetForDispute;

  mapping (uint256 => address) public arbitrators;
  mapping (address => bool) private arbitratorsReward;
  mapping (uint256 => bytes32) public votes;

  event ResultCommited(string);
  event VotesProvided();

  modifier onlyPoolMaster() {
    require(msg.sender == Pool(pool).poolMaster());
    _;
  }

  function Dispute(address _pool, bytes32 _argumentsHash, address _disputeCreator, uint _arbitratorsNumber) payable public {
    argumentsHash = _argumentsHash;
    pool = _pool;
    disputeCreator = _disputeCreator;
    blockForSeed = block.number + 1;
    arbitratorsNumber = _arbitratorsNumber;
  }

  function getSeed() public view returns(bytes32) {
    require(block.number > blockForSeed);
    return block.blockhash(blockForSeed);
  }

  function setResult(string _result) public onlyPoolMaster {
    require(votesProvided && !disputeResolved);
    result = _result;
    ResultCommited(result);
    disputeResolved = true;
    DRMInterface(DRMAddress).closeDispute();
    msg.sender.transfer(budgetForDispute.div(arbitratorsNumber + 1));
  }

  function getProfit() {
    require(arbitratorsReward[msg.sender]);
    arbitratorsReward[msg.sender] = false;
    msg.sender.transfer(budgetForDispute.div(arbitratorsNumber + 1));
  }

  function setArbitratorsAndVotes(bytes32[] _msgHash, uint8[] _v, bytes32[] _r, bytes32[] _s, string _result)   public returns(bool)  {
    for (uint i = 0; i < _msgHash.length; i++ ) {
      arbitrators[i] = validate(_msgHash[i], _v[i], _r[i], _s[i]);
      votes[i] = _msgHash[i];
    }
    votesProvided = true;
    VotesProvided();
    setResult(_result);
    return true;
  }

  function checkSha3(string messsage) public view returns (bytes32) {
    return keccak256(messsage);
  }

  function validate(bytes32 msgHash, uint8 v, bytes32 r, bytes32 s) view public returns (address) {
    bool ret;
    address addr;
    bytes memory prefix = "\x19Ethereum Signed Message:\n32";
    bytes32 prefixedHash = keccak256(prefix, msgHash);

    assembly {
    let size := mload(0x40)
    mstore(size, prefixedHash)
    mstore(add(size, 32), v)
    mstore(add(size, 64), r)
    mstore(add(size, 96), s)
    ret := call(3000, 1, 0, size, 128, size, 32)
    addr := mload(size)
    }
    return addr;
  }

  function testRecovery(bytes32 h, uint8 v, bytes32 r, bytes32 s) pure public returns (address) {
    //bytes memory prefix = "\x19Ethereum Signed Message:\n32";
    //bytes32 prefixedHash = keccak256(prefix, h);
    address addr = ecrecover(h, v, r, s);
    return addr;
  }


  function getResult() public view returns(string) {
    require(disputeResolved);
    return result;
  }

  // TO DO selfDestruct

/*
  function checkMessage(bytes32 _message, uint8 _v, bytes32 _r, bytes32 _s) returns (bytes32) {

  }
*/
  // TO DO service reward
  //function serviceReward() {}
}
