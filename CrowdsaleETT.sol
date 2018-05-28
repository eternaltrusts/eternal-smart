pragma solidity ^0.4.18;

// File: contracts/ERC20Token.sol

interface ERC20Token {
    function transfer(address _receiver, uint256 _amount);
    function decimals() returns(uint8);
    function getName() returns(bytes32);
    function balanceOf(address _to) returns(uint256);
}

// File: zeppelin-solidity/contracts/ownership/Ownable.sol

/**
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  function Ownable() public {
    owner = msg.sender;
  }

  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}

// File: zeppelin-solidity/contracts/token/ERC20/ERC20Basic.sol

/**
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
  function totalSupply() public view returns (uint256);
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

// File: zeppelin-solidity/contracts/token/ERC20/ERC20.sol

/**
 * @title ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/20
 */
contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender) public view returns (uint256);
  function transferFrom(address from, address to, uint256 value) public returns (bool);
  function approve(address spender, uint256 value) public returns (bool);
  event Approval(address indexed owner, address indexed spender, uint256 value);
}

// File: contracts/CrowdsaleETT.sol

/**
 * @title Crowdsale
 * @dev Crowdsale is a base contract for managing a token crowdsale,
 * allowing investors to purchase tokens with ether. This contract implements
 * such functionality in its most fundamental form and can be extended to provide additional
 * functionality and/or custom behavior.
 * The external interface represents the basic interface for purchasing tokens, and conform
 * the base architecture for crowdsales. They are *not* intended to be modified / overriden.
 * The internal interface conforms the extensible and modifiable surface of crowdsales. Override 
 * the methods to add functionality. Consider using 'super' where appropiate to concatenate
 * behavior.
 */

contract CrowdsaleETT is Ownable {
  // The token being sold
  ERC20 public token;

  bool public isBeneficiariesBlock1 = false;
  bool public isBeneficiariesBlock2 = false;
  bool public isBeneficiariesBlock3 = false;
  bool public isBeneficiariesBlock4 = false;

  address[] public beneficiaries;
  mapping (address => uint256) public beneficiariesTokens;
  mapping (address => bool) public isDeliverTokens;
  bool public isDeliverAll = false;

  address public walletApi;

  modifier onlyApi() {
    require(msg.sender ==  walletApi || msg.sender == owner);
    _;
  }

  /**
 * Event for token deliver logging
 * @param beneficiary who got the tokens
 * @param amount amount of tokens purchased
 */
  event DeliverTokens(address indexed beneficiary, uint256 amount);

  /**
 * Event for count token transfers
 * @param count count of tokens transfers
 */
  event TransferTokens(uint count);


  /**
   * @param _token Address of the token being sold
   */
  function CrowdsaleETT(ERC20 _token) public {
    require(_token != address(0));
    token = _token;
  }


  // -----------------------------------------
  // Crowdsale external interface
  // -----------------------------------------

  /**
   * @dev Delivery tokens of beneficiary
   * @param _beneficiary Beneficiary
   * @param _tokenAmount Tokens of beneficiary
   */
  function deliverTokens(address _beneficiary, uint256 _tokenAmount) onlyApi public {
    require(_beneficiary != address(0) && _tokenAmount > 0);
    _deliverTokens(_beneficiary, _tokenAmount);
  }

  /**
   * @dev Delivery tokens of beneficiaries
   * @param _beneficiaries List of beneficiaries
   * @param _tokenAmounts Tokens of beneficiaries
   */
  function deliverTokensByList(address[] _beneficiaries, uint256[] _tokenAmounts) onlyApi public {
    require(_beneficiaries.length > 0 && _beneficiaries.length == _tokenAmounts.length);
    for(uint i = 0; i < _beneficiaries.length; i += 1) {
      _deliverTokens(_beneficiaries[i], _tokenAmounts[i]);
    }
  }

  /**
   * @dev Transfer tokens by list beneficiaries
   * @param _part Count of beneficiaries for delivery of tokens (0 - all beneficiaries)
   */
  function transferTokens(uint _part) onlyOwner public returns(uint) {
    require(!isDeliverAll);
    uint count = 0;
    uint i;
    for(i = 0; i < beneficiaries.length; i += 1) {
      if (_part > 0 && count >= _part) {
        break;
      }
      address beneficiary = beneficiaries[i];
      if (!isDeliverTokens[beneficiary]) {
        uint256 tokenAmount = beneficiariesTokens[beneficiary];
        _deliverTokens(beneficiary, tokenAmount);
        isDeliverTokens[beneficiary] = true;
        count += 1;
      }
    }
    if (i == beneficiaries.length) {
      isDeliverAll = true;
    }
    TransferTokens(count);
    return count;
  }

  /**
   * @dev Set api wallet
   * @param _wallet Api address
   */
  function setApiWallet(address _wallet) onlyOwner public {
    require(_wallet != address(0));
    walletApi = _wallet;
  }

  /**
   * @dev Get count of beneficiaries
   */
  function beneficiariesCount() public view returns(uint) {
    return beneficiaries.length;
  }


  // -----------------------------------------
  // Internal interface (extensible)
  // -----------------------------------------


  /**
   * @dev Source of tokens. Override this method to modify the way in which the crowdsale ultimately gets and sends its tokens.
   * @param _beneficiary Address performing the token deliver
   * @param _tokenAmount Number of tokens to be emitted
   */
  function _deliverTokens(address _beneficiary, uint256 _tokenAmount) internal {
    ERC20Token(token).transfer(_beneficiary, _tokenAmount);
    DeliverTokens(_beneficiary, _tokenAmount);
  }

  /**
   * @dev Add tokens beneficiary to list for later deliver
   * @param _beneficiary Address performing the token deliver
   * @param _tokenAmount Number of tokens to be emitted
   */
  function addBeneficiary(address _beneficiary, uint256 _tokenAmount) internal {
    require(beneficiariesTokens[_beneficiary] == 0);
    beneficiaries[beneficiaries.length++] = _beneficiary;
    beneficiariesTokens[_beneficiary] = _tokenAmount;
  }

  /**
   * @dev Add beneficiaries with tokens to list for later deliver
   */
  function addBeneficiariesTokensBlock1() onlyOwner public {
    require(!isBeneficiariesBlock1);
    addBeneficiary(0xD62a9190784A69f6FdEf098cD8024584A58ea2E9, 40000000000000000000000);
    addBeneficiary(0x83eeef4a6b9791b10b2cd711de1cb4a4d00e8c62, 10000000000000000000000);

    addBeneficiary(0x7279Da8E9808adc053E856666151F118158c03e8, 30405000000000000786432);
    addBeneficiary(0x1e31d3A943cE21Acb39AAB9fe133F8f497068B1D, 50129000000000006029312);
    addBeneficiary(0xf6ba7d3e2223b395de88ebb04c868e1d0f5b6b43, 53341000000000002883584);
    addBeneficiary(0x1e0A516a0Ef4e6f53c897B74e3F836044744d29e, 320046000000000000524288);
    addBeneficiary(0x0AC444C5d6753462D4a2E7aBf75B22216C8260ce, 53341000000000002883584);
    addBeneficiary(0xC57CaC1301133b3B2ADeA17718E15718f904AEB9, 80629000000000004980736);
    addBeneficiary(0xFb726F750670d25FbbcB42BAc475A04A0e95C953, 30000000000000000000000);
    addBeneficiary(0x69Bfdee2A1b380919bA479Be7c4DdB9eA64d27EC, 40171999999999996854272);
    addBeneficiary(0xC13ecCd43CEd1dfdcCAEE396B9Eda0edF97F5788, 10042999999999999213568);
    addBeneficiary(0x073303B847DF2eAd257B91aA046c094B449A82c8, 426023849999999944359936);
    addBeneficiary(0x6eae49bd2A314C342E8AD606bc499C9a51635D7f, 10000000000000000000000);
    addBeneficiary(0x36d8e17F88b8b91A7931456e03E27C37bf27F143, 160687999999999987417088);
    addBeneficiary(0xe7bB73646Dc80414930fC549cE5Ba37e987f8039, 40171999999999996854272);
    addBeneficiary(0x5d98561752000e8986e0c595fc199a591bcec079, 20085999999999998427136);
    addBeneficiary(0xE0D2D7F7FC52EE30B0278249998558661Dae14E9, 120515999999999990562816);
    addBeneficiary(0xd2cf68aC7099dD5A4280597d6C1D4D25E519e1F9, 12051999999999998951424);
    addBeneficiary(0x6eC0F7396F10a36700dde967dE34fCC5AaCf7aE0, 30962999999999997116416);
    addBeneficiary(0x26d6bcdc51edb2be1c14017e438eaf3e18a42911, 80343999999999993708544);
    addBeneficiary(0x16147576070c241699d78Dec47e3dF08Eb83AE8c, 10000000000000000000000);
    addBeneficiary(0xEd1154145b6E2094aDf9CF6253042b98Dc849Ad6, 27000000000000002097152);
    addBeneficiary(0x4Fc3102F783bF8a20A2DebE30538601Eb013671E, 10000000000000000000000);
    addBeneficiary(0x438bC7005e5dB2eD207775FC16B3434a8E028eF7, 40171999999999996854272);
    addBeneficiary(0x8900a1948d103630586684f39f8BB6F860522044, 10000000000000000000000);
    addBeneficiary(0xd3B399444650A05811DAC6e114707cff0982f921, 34126999999999998164992);
    addBeneficiary(0x13Bb4b4f3cBEA813f8fcF18b6E44460a1b2E40Ea, 26800000000000000000000);
    addBeneficiary(0x050af9510651742d67e07ca3b51e2b68b35c7345, 1229463850000000015663104);
    addBeneficiary(0x494c2223c724fF72566C49370846885cAB60C975, 40171999999999996854272);
    addBeneficiary(0xc19561d86ed347fb6277645376FcC8b02b3dB710, 10000000000000000000000);
    addBeneficiary(0x7Cd13C82F3d5526822af5c00ae91ae9Dc5385ad5, 40171999999999996854272);
    addBeneficiary(0x5C31Ad35da16B347f2c3B8E28A4EeD81bD4538Ac, 10000000000000000000000);
    addBeneficiary(0x2048c1e4fE34AD15A5cAfEF5dF2F081d28152567, 10042999999999999213568);
    addBeneficiary(0x0c1B36ce935A2DcDCD2008B89B750dA21BB10E41, 20085999999999998427136);
    addBeneficiary(0xA0a06EE0418629A73FbFeBc355e48d345f5f60EF, 117458999999999992922112);
    addBeneficiary(0x06f01E8B7357F282E2F61e089fe6a0977a26D0eb, 15661000000000000786432);
    addBeneficiary(0xB47A064c9b328E061D02469CF4827277204dCd9B, 509835999999999954911232);
    addBeneficiary(0xCe26936F56658e1c7b670283fFdA7911EB72672A, 10000000000000000000000);
    addBeneficiary(0x81A6985A27cF9D15b5EDe6a7A552a7304F5Ef14a, 195765000000000004980736);
    addBeneficiary(0xDfe053d4d03e85B2247AA8b09bA3434200B4B69a, 39152999999999997640704);
    addBeneficiary(0x96CdA4525802B144937c79FCCB91F0367260614C, 789211999999999967494144);
    addBeneficiary(0x0f112e20Dd688093A7D1bE1937f0AA55Ab1865fC, 58730000000000001572864);
    addBeneficiary(0xC693DcF98A533461758f9002a3632694a57666Bc, 10000000000000000000000);
    addBeneficiary(0x82E22d13Ef71bBEBD02066bb3d7Ab75bD0f12e14, 10000000000000000000000);
    addBeneficiary(0x8Fbc85230ba297f2CcbE572C320eC6C23e570C56, 10000000000000000000000);
    addBeneficiary(0xbc4B9D0b8C33C32963a087E635da5A220B7a2782, 195765000000000004980736);
    addBeneficiary(0xeD8865581A6B9B3467E3118af9f3aA41bFEAe035, 3249699000000000089391104);
    addBeneficiary(0xB2C5B341670A79f9C8ed073D1Dd27D63C329E952, 59152999999999989252096);
    addBeneficiary(0xAD96f6F9DcE39216378938bB783D989a2F3A6215, 117458999999999992922112);
    addBeneficiary(0x0530Dc7986fd1E3dB5ABc6dA0869c3118534E616, 10000000000000000000000);
    addBeneficiary(0x1324aADB852c1865b569eE78d2a2BB46FA9178cb, 26179999999999998951424);
    addBeneficiary(0x214036Aff0B6F623ecA1912aFa7c4B2514c1d5bF, 10000000000000000000000);
    addBeneficiary(0x4e078D6C5398D3C350108920290a40ACaDC3345D, 10101000000000000786432);
    addBeneficiary(0xc0DE4CE11Dc8CA88532B6b083A3E9fE3eD22dc00, 10000000000000000000000);
    addBeneficiary(0xCd3E2AD86d411f6544f8Fa363A542Ce7688FEe06, 10102000000000000524288);
    addBeneficiary(0x8E77eEAaAe006DE9C47c2C6154f708daB8663f11, 62360000000000002097152);
    addBeneficiary(0x7714aE16dE6101B6165E008c88f685fA93352BfF, 93539999999999998951424);
    addBeneficiary(0x3571703b9b41df0cE079a015aD25e5Ab1B352208, 62360000000000002097152);
    isBeneficiariesBlock1 = true;
  }

  function addBeneficiariesTokensBlock2() onlyOwner public {
    require(!isBeneficiariesBlock2);
    addBeneficiary(0x5147e9Ac51ff9343D52766e364E6Bfc4BAc1bD01, 10040000000000000000000);
    addBeneficiary(0x33529c45182B61C9d8cbbcdb8a747Be5e106d306, 187079999999999997902848);
    addBeneficiary(0x011Ae58f16Ba6CFb53e2e27E7b753E88d41Df9A3, 215926999999999975096320);
    addBeneficiary(0xf7Eab72Ee14daD3DFEf597420F669c25B39f938C, 31180000000000001048576);
    addBeneficiary(0x845fDe42FC0364FAa25f54db71e2720b06977C70, 10288999999999999737856);
    addBeneficiary(0x1e42356724d70794ac233aa7ad8b4d34c3b4460e, 124720000000000004194304);
    addBeneficiary(0x6D59E3c0B0177Fe4FEb48004b4cbd212955514be, 16525000000000000786432);
    addBeneficiary(0x0cFe6CF67139f5AF4d2D334b89b143a5b08f29E8, 10288999999999999737856);
    addBeneficiary(0xA77899Edf452f66F3A0516B8fff2f9b61f26c7c3, 56123999999999992659968);
    addBeneficiary(0x6a5b3D6ECBC2fDC9abf3799A12c1ED8c756Ab4c2, 187079999999999997902848);
    addBeneficiary(0xFf8fC236168D247d48e60E7951599ba631887697, 10000000000000000000000);
    addBeneficiary(0xDbA67a524CD706B5A67EF31289d1B15ce3D12A0A, 1094807999999999943376896);
    addBeneficiary(0x7a33cdA3Da217a49Df8ac3f82e1c3B2856306427, 2667000000000000262144);
    addBeneficiary(0x2C0fA44e71bf9169bf46385aE4798690D3363ae9, 53341000000000002883584);
    addBeneficiary(0xca4a2b686dd7d66df6f544ee1d147872a5fa398c, 10000000000000000000000);
    addBeneficiary(0xe6e757753628682C49Ae4604636f029B9A7aa9E9, 16002000000000001572864);
    addBeneficiary(0xd184Afe5F34E34AB68572EC0c5Ec3132A02ccA60, 10080999999999999737856);
    addBeneficiary(0x273F365db20605e38E0250dA05b51f339A7DA839, 21336000000000002097152);
    addBeneficiary(0x8ab5084fB5362e8f35F0FBAA488F6283e0312266, 10668000000000001048576);
    addBeneficiary(0xa690d6eD1fA511Ee7ECe5D24ED36537B516d3492, 10000000000000000000000);
    addBeneficiary(0xEd8fFd3c9c885F5D886A5328D9d2D592dd425c01, 10000000000000000000000);
    addBeneficiary(0x6D8fA26C0C09E7332C24E92D048067581f3ff832, 33334999999999996067840);
    addBeneficiary(0x356FdFc648785e32bB796048131B0bb1bAcFEF2d, 49999999999999995805696);
    addBeneficiary(0xe2fEF09d37f4Aa67aBe47F7f72870B4539dE4E76, 22001999999999999475712);
    addBeneficiary(0x3135292FdC1CE2E336A487438823910196127F2D, 10000000000000000000000);
    addBeneficiary(0xCf3DCe87158508a88a06a0039cCd8622f6553E00, 48005999999999994232832);
    addBeneficiary(0x473D617F29bC57cAc9a3636B0429a4B3771e8605, 160023000000000000262144);
    addBeneficiary(0x1EE655FE1BC39546Ca075f562Ab871AB5F7b5F6b, 2000000000000000000000);
    addBeneficiary(0xC6F1D6dDf173Ea43C737e0E3A8859A7E6abE2678, 2000000000000000000000);
    addBeneficiary(0x30423F26733Aa686503620c45347f4E5b568a6D0, 10000000000000000000000);
    addBeneficiary(0x5193A342A40c0dec98B6Ec4E350dCbB04FaD5BE4, 30000000000000000000000);
    addBeneficiary(0xC82510889E15Fe58a88A7B9263fb587026982c4F, 20000000000000000000000);
    addBeneficiary(0x03d7e2d4222990a65286ECeA611714B340573733, 9200000000000000000000);
    addBeneficiary(0x37d0F3a55ffc4C2898B2952F6322281af079b20C, 128017999999999999475712);
    addBeneficiary(0x3D86C8A928E9595114e01bb0539bdD69e9EfDF3B, 76670999999999989776384);
    addBeneficiary(0x9f03840D4508E515125Bc4c10A20911a2f38A4Cd, 136008999999999974572032);
    addBeneficiary(0xD3e075458b142335d87E2157dFeCEc27A11f2515, 18146614200000002178154496);
    addBeneficiary(0x1383f83C07E5e4BC67F7Ac9b5e8Be691dD612D40, 26670999999999998164992);
    addBeneficiary(0xc12A519E1a3620792bc40A9E400D2f0357165bc8, 261000000000000000000);
    addBeneficiary(0x5B1aC9DDa16679B8e0bf57C987E0CF9727a25297, 10000000000000000000000);
    addBeneficiary(0xcA8793bAD940Dc9E972b5A3D3546015a1aF73037, 26670999999999998164992);
    addBeneficiary(0xF5d4767917E0c9c422BC5B4833902DE3011DA5bd, 10000000000000000000000);
    addBeneficiary(0xeda7f9bb20783c1dc1f88ebfa81eafab1df9acf5, 26654000000000000524288);
    addBeneficiary(0x674939B69d32906f90CCcF9fC107532711f82D09, 15000000000000000000000);
    addBeneficiary(0xb0868F8c14d15335E5D5a8Ddf5d61937DFaFC864, 26670999999999998164992);
    addBeneficiary(0x356FdFc648785e32bB796048131B0bb1bAcFEF2, 10000000000000000000000);
    addBeneficiary(0xd18B4E17de80a8998b4d2eB9ec02d4fEBBb00F06, 53341000000000002883584);
    addBeneficiary(0x2654175DB4cDc3821a2c6c0209aFAcd8434a194D, 80000000000000000000000);
    addBeneficiary(0xCE2ABa88baF7658383B33b828c64738b85eFAEb2, 11169603900000002331639808);
    addBeneficiary(0x949EE306A60C62DA4b1fc4b746E75A3Dab0f627f, 10000000000000000000000);
    addBeneficiary(0x144911439d867FeCB985e38df80357E2A56473CF, 30403999999999998951424);
    addBeneficiary(0x496236DA480737487766aDBC4035C4d1DF2662cf, 258704000000000029360128);
    addBeneficiary(0xA72D94596B59E675b8DbBF428d98ddA0e5FE9cc4, 11735000000000000262144);
    addBeneficiary(0x2963b9ee4BdE27a0E71B5f393E0153a55405155C, 15661000000000000786432);
    addBeneficiary(0xF4BB7f073Ef06cE60c538e2CB8B8669bD66Eb635, 10000000000000000000000);
    addBeneficiary(0xE15Ea5F3fAC703eF01b9BEC81aF518703C44f5d5, 75000000000000002097152);
    addBeneficiary(0x2ab20799129B3D84c23bC7d1eEeC33d12384a209, 234917999999999985844224);
    addBeneficiary(0xcCBedE2CC6A521a1cab36d935577b751af8DDa78, 12920000000000000000000);
    isBeneficiariesBlock2 = true;
  }

  function addBeneficiariesTokensBlock3() onlyOwner public {
    require(!isBeneficiariesBlock3);
    addBeneficiary(0x336755f8A288e94434484E61Aae118b347E02d49, 234917999999999985844224);
    addBeneficiary(0x64b1D0CfaBd1a067EC3bb8CF55ddBd6FD60822d9, 234917999999999985844224);
    addBeneficiary(0xff96d7530a8d8A584232c6ab1e8ae685c98B653A, 10179999999999998951424);
    addBeneficiary(0x145080e99c57755c7f7Ce6e54bB0Bdbd185eEA9e, 33280000000000000000000);
    addBeneficiary(0x300a0F4665652770507aA92FD2961f65051ba1eC, 77148999999999994494976);
    addBeneficiary(0xe523db8F195B741285586bA5cc5CD6e2b495764D, 10000000000000000000000);
    addBeneficiary(0xde45796b41D2fCff06f10e9a42782b13D70aa556, 39101999999999996329984);
    addBeneficiary(0x23e12b64D6690cB22fe90F6254a60180A0dD6F50, 12048999999999999737856);
    addBeneficiary(0xb8A6D291F3453C0f95F220f111199132Ec6918A4, 39719999999999997902848);
    addBeneficiary(0xB74995A7E63F6476f9282Bf56a7B0D9677E9A775, 10384000000000000000000);
    addBeneficiary(0x205793E02Ab3a23F566C7ca9C22844FfD0600A9c, 304517000000000017563648);
    addBeneficiary(0x34891b4978c4346216952C9a877B9de3161E6A09, 2433878999999999748603904);
    addBeneficiary(0x5c17Fa0e436Fc2EDd4B8a3144c4Ca95145E424E7, 42023999999999997902848);
    addBeneficiary(0x214b39177fb6861998f87cedcf8e8e1bf166d5dd, 10000000000000000000000);
    addBeneficiary(0xFc47562fad1537145245aeee8014596274B71E2b, 127331999999999998951424);
    addBeneficiary(0x8404f438799c642226dD868ad4189F006934f805, 32024000000000002097152);
    addBeneficiary(0x7EdEA9Ff57625D4112778D5D69e77c6EC007D585, 10000000000000000000000);
    addBeneficiary(0x67E472c1A9DE0389B034595D9791b770e0980915, 84938000000000001572864);
    addBeneficiary(0x4eC3226959B6939a41c21FB0486D76f368B01d11, 895735999999999985319936);
    addBeneficiary(0x073303b847df2ead257b91aa046c094b449a82c8, 489889999999999978504192);
    addBeneficiary(0xC6484EE9BAc70C3E98A7142475A46Bdd29E4D942, 10172000000000001048576);
    addBeneficiary(0x0C61d26aDC595b61592e5ff197eDD7bCF0d612B9, 10146999999999999213568);
    addBeneficiary(0x67dd4879Abf7D0c673A7fd2c9B1167953484eCbE, 10274999999999999213568);
    addBeneficiary(0x29F920b87f60F3C6599f42a824aAE002AB4a44B6, 20000000000000000000000);
    addBeneficiary(0xbc4b9d0b8c33c32963a087e635da5a220b7a2782, 255909999999999985844224);
    addBeneficiary(0x170fed625ac55026aa5d74667105157cc4695788, 10257999999999999475712);
    addBeneficiary(0x90508fe56BbFAf9878C7ea32e9Dd87F6f1A851e4, 630000000000000037748736);
    addBeneficiary(0x452037Fbb68aE019FA33137eABb7B8D010E472d5, 10444000000000001048576);
    addBeneficiary(0x18216b87F0B625717DDc33A06dE0dA51913EC444, 205356000000000013631488);
    addBeneficiary(0x49c82f8c2400d0e70c82039ceaf313b2d047a11e, 49020000000000001048576);
    addBeneficiary(0x24318b0bcdd034215c0e312eedb5e9d6b4700504, 255400000000000006291456);
    addBeneficiary(0x0dF363C1F92f50560878Aa475A762299b595030f, 25738999999999999213568);
    addBeneficiary(0x60C14008b5ec8Bab7182e4442cA2898e4A940d24, 15456000000000000000000);
    addBeneficiary(0xBD7b9636929474c72357f93807C6C5dF0035f8a2, 101486000000000000524288);
    addBeneficiary(0x2134e023C347CC1ce59534485142169E6cA1ea94, 53127999999999997902848);
    addBeneficiary(0x9f0Ff0789939D849cB803DE6cc06c0F0F5b99beC, 10188000000000001048576);
    addBeneficiary(0xCEB4c5029E4b74edd74EE7fF3ae159C6Dd4a720A, 26810000000000001572864);
    addBeneficiary(0x8A31A8b898d6554AB3935c27C2433D538EE0F6fB, 53620000000000003145728);
    addBeneficiary(0x34c172989d94d85288C3B2fB91189780972812D4, 122063999999999995805696);
    addBeneficiary(0x57D6c165D838d4A1DAC3b46a571f41C880A50583, 12938999999999999213568);
    addBeneficiary(0xa5f2f069DD55cAafF98Fabd4Ca05b83cDC511f30, 61292999999999998689280);
    addBeneficiary(0x388B4cc5C860FBd28E6F6934b0339fDfE0e83424, 29982999999999998164992);
    addBeneficiary(0x273b5834581BE752601fdbD76Da111E39c6A94B2, 93539999999999998951424);
    addBeneficiary(0x03184BD36C8c13EeC14eBfcD1487316e753fc5F2, 12472000000000000000000);
    addBeneficiary(0x35e60350C930B05B5293D460a68d94F25Af2c90f, 37415999999999997902848);
    addBeneficiary(0x8566bda9095bbc3734cde35fe9c44322733815e8, 31180000000000001048576);
    addBeneficiary(0xc5cD2bA17e48c4410C59C61c666EC339A6E569E2, 62360000000000002097152);
    addBeneficiary(0x45202a1e6d672b20a3c64957aacd502e90a5858a, 10002999999999999213568);
    addBeneficiary(0xc99e93F6943Ab3a83372a4cfc2dbbb272c8974da, 10226999999999999213568);
    addBeneficiary(0xCbe89B06DA7BD0eb27879D6D0638809bBBbe03FD, 24944000000000000000000);
    addBeneficiary(0x6f5D19286799D3b7737321312620E3D023D7EBc1, 62360000000000002097152);
    addBeneficiary(0xcacf88992a543625503a9a5913b50743d28df44e, 62360000000000002097152);
    addBeneficiary(0xcbe4dc720f42998d3ab934d7ada7260683b55c90, 31180000000000001048576);
    addBeneficiary(0x50e5D90dF8b4FFEa8a1a9A2a37095491e10c21F8, 10102000000000000524288);
    addBeneficiary(0xEE78548661D0D823CABf700c565BACb43f43677b, 11224999999999999737856);
    addBeneficiary(0x2ec698480f860dcd4d6e78f5fc13f94739cb032f, 12000000000000000000000);
    addBeneficiary(0x79E95F5b9679cA97da6823864548b223024F56FF, 10600999999999999737856);
    addBeneficiary(0xF603A67f66deAC54F0aC90daC3e6d0aC58C07ba8, 10000000000000000000000);
    isBeneficiariesBlock3 = true;
  }

  function addBeneficiariesTokensBlock4() onlyOwner public {
    require(!isBeneficiariesBlock4);
    addBeneficiary(0x7828c9686862fBC4e35F6F8b05ad99A77C2e10b4, 99776000000000000000000);
    addBeneficiary(0x094b6692c4eeA9B3882eB2e0d8a0d912c59CC3Ca, 19299999999999998951424);
    addBeneficiary(0x6E9AEE5787F2B1948FD3De0212DA4F3F6a555Eb8, 311799999999999985319936);
    addBeneficiary(0x1E7FF1B31586d44B69cbdE9bd859AB060e912217, 118484000000000003145728);
    addBeneficiary(0xa888161082b35fa8e1df323bbc80bcd7fbb539b3, 62360000000000002097152);
    addBeneficiary(0x6278A501FaCF33bFda94E0ad0aa40Cc9bBf4783a, 14343000000000000262144);
    addBeneficiary(0x19351545207b9e3d2cfd3bc32863eafe30431220, 5249999999999999777701888);
    addBeneficiary(0x51c51ce8f7fcd8cfc6c21ad70e9922bc241d8068, 118484000000000003145728);
    addBeneficiary(0x31E6902938cFC911E5C6b1FaE2486395F49f97a9, 31180000000000001048576);
    addBeneficiary(0x51C51CE8f7fCD8cfC6C21ad70E9922Bc241d8068, 118484000000000003145728);
    addBeneficiary(0x201013324AA3Ba025d57b18210733abe4b002508, 10040000000000000000000);
    addBeneficiary(0x4c406D550B80Fb613c1A874a9757Cb3412CC896B, 10288999999999999737856);
    addBeneficiary(0x2a44cf4f461bb8325c57a0f0c6958d98272537da, 62360000000000002097152);
    addBeneficiary(0xE23eA5c6CB58B6693c0a47C3bDb0c4853C604010, 661327799999999997116416);
    addBeneficiary(0x222984e1BaaeE01AF26740B4327976618Fc1B0C0, 33600000000000000000000);
    addBeneficiary(0x19b9a529e4ddA3e8e437DbC90f140Bc1A88654F3, 10030000000000000524288);
    addBeneficiary(0xe9c63d8DF419528184c5B0CF2bE886a9D594AF82, 10226999999999999213568);
    addBeneficiary(0xc1556AC288159f577b1AC03f33399815c0BDa8d3, 10000000000000000000000);
    addBeneficiary(0x3D3829d534BFb65199dA0c3E7fC7815ec98Dda01, 145482000000000001572864);
    addBeneficiary(0x1a1482d32c86425f87d32bdbeda9a7ff494b386e, 10236000000000001048576);
    addBeneficiary(0xdba67a524cd706b5a67ef31289d1b15ce3d12a0a, 1042910000000000055050240);
    addBeneficiary(0x0474EaaF8a3f2ab1AFf8E6e09D26Cf031270F4dB, 88563000000000001310720);
    addBeneficiary(0x2de4652a1358F193F9C0D68fF78CAbbbc558dc99, 72202000000000001572864);
    addBeneficiary(0xb22818c9Af151ff8dADC3Ea118F4778dA3142c11, 17682999999999999213568);
    addBeneficiary(0x91eb632498dF6B313E599859e4f15aD742816da9, 29276000000000001048576);
    addBeneficiary(0x51a3Bc5Ce0E270EACd99eB8636AAA8FF19860e76, 14540000000000001048576);
    addBeneficiary(0xD3e5A0C72Dd64F01B51446A17eAa9F27E370DC6C, 14529999999999999475712);
    addBeneficiary(0xe3f3D549886B272620a033f79056Ad856fc915cC, 72700000000000001048576);
    addBeneficiary(0xFCEFc95ADf8a1e906a911c527b15a92c1f434405, 10000000000000000000000);
    addBeneficiary(0x8d0bA9A768f2495361E14B1e1030DDE0bE1A7083, 10000000000000000000000);
    addBeneficiary(0xdE6B60f1b002Fc48DDCCb86CaE565e8E826D3b24, 16160000000000000000000);
    addBeneficiary(0x0C65CadeC0DDFBe65B9620eF0fe28d212F26Ee49, 10122999999999999213568);
    addBeneficiary(0xd9F29A3eae7E75E22dB51DE860E619f39B9c939e, 42172000000000001048576);
    addBeneficiary(0xB6e331A43e0d4DE2f855fB4B754343DB37B496a0, 10078000000000000524288);
    addBeneficiary(0x3e6686667ea6e2b77f0f5d59dd6fe295ead5e5f8, 42730000000000001572864);
    addBeneficiary(0x58996c9f9C797376568732ff0DE4f8236dC2A458, 70124999999999998689280);
    addBeneficiary(0x1252767daE60e0788DE737d4a8781918D036A1eb, 20229999999999998427136);
    addBeneficiary(0x24e9B4d50f32b120046f5Aa50Fc916bBdC3AC35f, 10000000000000000000000);
    addBeneficiary(0x1adE2Afe27e9C63370943102a0a74716D6403E57, 10000000000000000000000);
    addBeneficiary(0x2AD4970F97366F2ed13057d9348606F3412B1Ed5, 34170000000000001572864);
    addBeneficiary(0x9fedcb48a7f43b475d17c9dabf9c61975df8058a, 10000000000000000000000);
    addBeneficiary(0x9E5652190faE1E27102C2DB012ea7805aAa1B0ca, 67394000000000003670016);
    addBeneficiary(0xf79878ad3300b58a5012566121b89cf08f13c8e3, 27100000000000001048576);
    addBeneficiary(0xc64977219492C2fd78Dcd5ABfcF73785ecfF4e7e, 10000000000000000000000);
    addBeneficiary(0x0a71ba0558b78b7bd834e81cdc286bdfbda227c9, 10000000000000000000000);
    addBeneficiary(0x6922A3671Bb8F1F8341b77792750B87fbd05a1D1, 10000000000000000000000);
    addBeneficiary(0xabf8aF5a40Af6F34880dF10f44EE9fD530a6FC3c, 10000000000000000000000);
    addBeneficiary(0xb7FaB9e5D70c2F0a147C221947CcB32779f35952, 144181999999999998427136);
    addBeneficiary(0x3910b81d96bb98480980b6270858bbec05adc14d, 35760000000000000000000);
    addBeneficiary(0xb33878E6E3584C00f1aa5f3085B8A9D0f1f2B303, 69594999999999999213568);
    addBeneficiary(0x090aCd31bb9e59d816c568E8322f8f87cF885125, 69850999999999999213568);
    addBeneficiary(0xDCee0348283bd64DE022193A94E3fB694AEfCe96, 99999999999999991611392);
    addBeneficiary(0x23ce308268162fE35C6Cb6c96583cB9395e6Dc59, 20133999999999998427136);
    addBeneficiary(0x587e48bb274eea79b55bf0734f4f331bda522d66, 10047000000000000262144);
    addBeneficiary(0xC40Ab96791843cFe128740EBa443Cd185C2400F2, 10211999999999998951424);
    addBeneficiary(0x934DbEd4E321fcB1E81A2E3FA83Ef32D93150943, 10000000000000000000000);
    addBeneficiary(0xC6a8c41469c4f6f194B62cAE82BE7a475927BF99, 54318000000000000524288);
    isBeneficiariesBlock4 = true;
  }
}
