pragma solidity ^0.4.0;


contract PermissionsNames {

  mapping (bytes32 => uint) public namesMapping;
  address owner = msg.sender;

  function PermissionsNames() {
    owner = msg.sender;
  }

  modifier onlyOwner {
    require(msg.sender == owner);
    _;
  }

  function setPermissionLevel(bytes32 name, uint level) onlyOwner {
    namesMapping[name] = level;
  }
}