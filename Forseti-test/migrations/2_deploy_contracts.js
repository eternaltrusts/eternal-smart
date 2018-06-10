var Pool = artifacts.require("./Pools/Pool.sol");
var Dispute = artifacts.require("./DRM/Dispute.sol");
var Fors = artifacts.require("./Fors.sol");
var PoolFactory = artifacts.require("./Pools/PoolFactory.sol");



var wallet = '0x627306090abab3a6e1400e9345bc60c78a8bef57';
var token = '0xDbCf7344F1387C77089C3081F4513d0A1eDe3FF2';


module.exports = function (deployer) {
    deployer.deploy(Pool, wallet, 10000000000000000000, "test").then(function () {
        return deployer.deploy(Dispute, Pool.address,"sadsa", wallet, 1 );
    })/*.then(function () {
        return deployer.deploy(DRM);
    })*/
};

