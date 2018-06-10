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
Configure = {
    "alias":"TrinityNode",# you can rename your node
    "GatewayURL":"http://localhost:8077",
    "AutoCreate": True, # if the wallet accept the create channel request automatically
    "Channel":{
        "TNC":{
            "CommitMinDeposit": 1,   # the min commit deposit
            "CommitMaxDeposit": 5000,# the max commit deposit
            "Fee": 0.01 # gateway fee
        },
        "NEO": {
            "Fee": 0    # must be integer
        },
        "GAS": {
            "Fee": 0.001
        }
    },#
    "MaxChannel":100, # the max number to create channel, if 0 , no limited
    "NetAddress":"localhost",
    "RpcListenAddress":"0.0.0.0",
    "NetPort":"20556",
    "GatewayTCP":"localhost:8089",
    "AssetType":{
        "TNC": "0x849d095d07950b9e56d0c895ec48ec5100cfdff1",
        "NEO": "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
        "GAS": "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
    },
    "BlockChain":{
        "RPCClient":"http://localhost:20332", # neocli client json-rpc
        "NeoProtocol":"/home/will/neocli/protocol.json",
        "NeoUrlEnhance": "http://47.254.64.251:21332",
        "NeoNetUrl" : "http://47.254.64.251:20332"
    },
    "DataBase":{"url": "http://localhost:20554"
    },
    "Version":"v0.2.1",
    "Magic":{
        "Block":1953787457,
        "Trinity":19990331
    }
}