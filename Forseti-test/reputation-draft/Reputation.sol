pragma solidity ^0.4.0;

import "./Permissions.sol";


contract Reputation  {


  struct Profile {
  // categoryName => reputationValue
  mapping (string => int) reputationByCategories;
  // [ dealAddress => reputationChangeValue ]
  mapping (address => int) reputationChangeHistory;
  }

  mapping (address => Profile) profiles;
  bytes32 levelToChangeRep;
  address permissionsContractAddress = 0x0;

  function Reputation(address _permissionsContractAddress) {
    permissionsContractAddress = _permissionsContractAddress;
  }

  event Log(address);

  function change(address userAddress, int value, string category)  {
    address dealAddress = msg.sender;
    require(Permissions(permissionsContractAddress).checkPermission(dealAddress,"changeReputation"));
    profiles[userAddress].reputationChangeHistory[dealAddress] = value;
    profiles[userAddress].reputationByCategories[category] += value;
  }

  function getRep(address userAddress, string category) returns(int) {
    require(Permissions(permissionsContractAddress).checkPermission(msg.sender,"getReputation"));
    return profiles[userAddress].reputationByCategories[category];
  }
}
