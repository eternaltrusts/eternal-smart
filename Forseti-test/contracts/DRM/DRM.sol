pragma solidity ^0.4.18;

import './Dispute.sol';

contract DRM {

  mapping (address => bool) public activeDisputes;
  mapping (uint256 => address) public IdDisputes;
  uint256 public disputesCounter;

  event DisputeCreate(address _diputeCreator, address _dispute, address _pool);

  function createDispute(address _pool, bytes32 _argumentsHash, uint _arbitratorsNumber) payable public {
    address newDispute = (new Dispute).value(msg.value)(_pool, _argumentsHash, msg.sender, _arbitratorsNumber);
    disputesCounter +=1;
    activeDisputes[newDispute] = true;
    IdDisputes[disputesCounter] = newDispute;
    DisputeCreate(msg.sender, newDispute, _pool);
  }

  function closeDispute() public {
    activeDisputes[msg.sender] = false;
  }


}