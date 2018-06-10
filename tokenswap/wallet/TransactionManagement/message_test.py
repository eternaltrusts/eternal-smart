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
#coding=utf-8

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import unittest
from wallet.TransactionManagement.message import RegisterMessage
from lightwallet.Nep6Wallet import Nep6Wallet

path = os.path.dirname(os.path.abspath(__file__))
TestWallet = os.path.join(path,"testwallet")
WalletPassword = "1234567890"

class TestRegisterMessage(unittest.TestCase):
    TestMessage = { "MessageType":"RegisterChannel",
    "Sender": "9090909090909090909090909@127.0.0.1:20553",
    "Receiver":"101010101001001010100101@127.0.0.1:20552",
    "ChannelName":"090A8E08E0358305035709403",
    "MessageBody": {
            ""
            "AssetType": "Tnc",
            "Deposit":"10",
        }
    }
    def setUp(self):
        if os.path.isfile(TestWallet):
            self.Wallet = Nep6Wallet.Open(TestWallet, WalletPassword)
        else:
            self.Wallet = Nep6Wallet.Create(TestWallet, WalletPassword)


    def test01_handle_message(self):
        register = RegisterMessage(self.TestMessage, wallet=self.Wallet)
        result = register.handle_message()


if __name__ == "__main__":

    unittest.main()





