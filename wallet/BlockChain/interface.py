"""Author: Trinity Core Team 

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
import requests
from TX.utils import pubkeyToAddressHash,pubkeyToAddress
from wallet.configure import Configure
from log import LOG
import json


AssetType=Configure["AssetType"]


NetUrl = Configure['BlockChain']['NeoNetUrl']

class InterfaceRpc(object):
    RequetsID = 0

    @classmethod
    def ID(cls):
        cls.RequetsID +=1
        return cls.RequetsID


def get_block_count():
    request = {
  "jsonrpc": "2.0",
  "method": "getblockcount",
  "params": [],
  "id": InterfaceRpc.ID()
}

    result = requests.post(url = NetUrl, json = request)
    return result.json()["result"]


def send_raw(raw):
    request =  { "jsonrpc": "2.0",
  "method": "sendrawtransaction",
  "params": [raw],
  "id": InterfaceRpc.ID()}

    result = requests.post(url=NetUrl, json=request)
    if result.json().get("result") is not None:
        return result.json()["result"]
    else:
        return result.json()


def get_bolck(index):
    request = {
  "jsonrpc": "2.0",
  "method": "getblock",
  "params": [int(index), 1],
  "id": InterfaceRpc.ID()
}
    result = requests.post(url=NetUrl, json=request)
    return result.json()["result"]


def get_balance(pubkey, asset_type):
    if len(asset_type) >10:
        asset_script = asset_type
    else:
        asset_script = AssetType.get(asset_type.upper())
    asset_script = asset_script.replace("0x","")
    if asset_script == "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b":
        return get_balance_extend(pubkeyToAddress(pubkey),"NEO")
    elif asset_script == "602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7":
        return get_balance_extend(pubkeyToAddress(pubkey),"GAS")

    address_hash = pubkeyToAddressHash(pubkey)

    def convert_hash(hash):
        t = hash[-2::-2]
        t1 = hash[::-2]
        s = ["".join(i) for i in zip(t, t1)]
        return "".join(s)

    request ={
        "jsonrpc": "2.0",
        "method": "invokefunction",
        "params": [
            asset_script,
            "balanceOf",
            [
                {
                    "type": "Hash160",
                    "value": convert_hash(address_hash)
                }
            ]
        ],
        "id": InterfaceRpc.ID()
    }
    result = requests.post(url=NetUrl, json=request)
    if result.json().get("result"):
        value = result.json().get("result").get("stack")[0].get("value")
        if value:
            return hex2interger(value)
    return 0


def get_balance_extend(address, asset_name="NEO"):
    asset_type = {"NEO":"neoBalance",
                  "GAS":"gasBalance"}
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "jsonrpc": "2.0",
        "method": "getBalance",
        "params": [address],
        "id": 1
    }
    result = requests.post(Configure["BlockChain"]["NeoUrlEnhance"], headers=headers, json=data).json()
    if result.get("result"):
        try:
            return result.get("result").get(asset_type.get(asset_name))
        except Exception as e:
            LOG.error(str(e))
            return 0
    LOG.error(json.dumps(result))
    return 0


def get_application_log(tx_id):
    request = {
        "jsonrpc": "2.0",
        "method": "getapplicationlog",
        "params": [tx_id],
        "id": InterfaceRpc.ID()
    }

    result = requests.post(url=NetUrl, json=request)
    LOG.debug(result)
    return result.json()["result"]


def check_vmstate(tx_id):
    try:
        result = get_application_log(tx_id)
        return "FAULT" not in result["vmstate"]
    except KeyError as e:
        LOG.error(str(e))
        return False


def hex2interger(input):
    tmp_list=[]
    for i in range(0,len(input),2):
        tmp_list.append(input[i:i+2])
    hex_str="".join(list(reversed(tmp_list)))
    output=int(hex_str,16)/100000000

    return output