pragma solidity ^0.4.0;

import "./PermissionNames.sol";


contract PermissionNamesExtension {

  address owner = msg.sender;
  address permissionNamesContractAddress = 0x0;
  modifier onlyOwner {
    require(msg.sender == owner);
    _;
  }

  function setPermissionNamesContractAddress(address _permissionNamesContractAddress) onlyOwner {
    permissionNamesContractAddress = _permissionNamesContractAddress;
  }

  function getLevelbyName(bytes32 name) returns(uint) {
    return PermissionsNames(permissionNamesContractAddress).namesMapping(name);
  }
}