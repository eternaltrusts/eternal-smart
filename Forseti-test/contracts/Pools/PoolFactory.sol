pragma solidity ^0.4.18;

import "../dependencies/ERC20.sol";
import "../dependencies/Ownable.sol";
import "./Pool.sol";

contract PoolFactory {

  mapping (uint => address) public pools;
  uint256 public poolsCount;
  //uint256 depositValue;
  ERC20 public forsToken;


  event NewPoolCreating(address newPool, address newPoolsMaster);


  function PoolFactory(address _token) public {
    forsToken = ERC20(_token);
    //depositValue = _depositValue;
  }


  function createPool(uint256 _depositStake, string _name) public {
    // require()
    address newPool = new Pool(msg.sender, _depositStake, _name);
    poolsCount += 1;
    pools[poolsCount] = newPool;
    forsToken.transferFrom(msg.sender, newPool, _depositStake);
    NewPoolCreating(newPool, msg.sender);
  }
}