pragma solidity ^0.4.18;

import "../dependencies/SafeMath.sol";

contract Pool {

  using SafeMath for uint256;

  modifier onlyPoolMaster() {
    require(msg.sender == poolMaster);
    _;
  }

  struct Member {
  uint256 reputationPoints;
  address ethAddress;
  }

  address public poolMaster;
  uint256 public depositStake;
  uint256 public membersLimit;
  string public name;

  mapping (uint256 => Member) public membersById;
  mapping (address => uint256) public membersByAddress;
  //mapping (uint256 => Member) public pendingMembers;
  uint256 public membersCount;
  //uint256 public pendingCount;
  //Member[] pendingMembers;

  function Pool(address _poolMaster, uint256 _depositStake, string _name) public {
    name = _name;
    poolMaster = _poolMaster;
    depositStake = _depositStake;
    membersLimit = depositStake.div(1 ether);
  }

  function becomeNewMember() public  {
    //pendingMembers[pendingCount + 1] = Member(1 , msg.sender);
    //pendingCount += 1;
    membersCount += 1;
    membersById[membersCount] = Member(1 , msg.sender);
    membersByAddress[msg.sender] = membersCount;
  }

  function leavePool() public {
    uint256 idToDelete;
    idToDelete = membersByAddress[msg.sender];
    delete membersByAddress[msg.sender];
    delete membersById[idToDelete];
  }

  /**
  function confirmNewMember(uint256 id) public onlyPoolMaster {
    membersId[membersCount + 1] =  pendingMembers[id];
    membersCount += 1;
    delete pendingMembers[id];
    pendingCount -= 1;
  }
  */

  function getMembersReputation(uint256 _id) public view returns(uint256) {
    return membersById[_id].reputationPoints;
  }

  function getMembersAddress(uint256 _id) public view returns(address) {
    return membersById[_id].ethAddress;
  }


}
// need check confirmNewMember