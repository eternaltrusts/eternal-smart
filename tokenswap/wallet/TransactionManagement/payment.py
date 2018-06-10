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
import base58
from wallet.configure import Configure
from log import LOG
import json
import binascii
import hashlib
from Crypto import Random



class Payment(object):
    """

    """
    HashR={}
    HashHistory = {}

    def __init__(self, wallet, remark=None):
        self.wallet = wallet
        self.remark = remark

    def generate_payment_code(self,asset_type, value, comments):
        if len(asset_type) == 40:
            asset_type = asset_type
        elif len(asset_type) == 42:
            asset_type = asset_type.replace("0x","")
        else:
            asset_type = Configure.get("AssetType").get(asset_type.upper())
        hr = self.create_hr()

        code = "{uri}&{hr}&{asset_type}&{value}&{comments}".format(uri=self.wallet.url,
                                                                   hr=hr, asset_type=asset_type,
                                                                   value=str(value),comments=comments)
        base58_code = base58.b58encode(code.encode())
        return "TN{}".format(base58_code)

    @staticmethod
    def decode_payment_code(payment_code):
        if not payment_code.startswith("TN"):
            LOG.error("payment code is not trinity payment")
            return False, None
        base58_code = payment_code[2:]
        code = base58.b58decode(base58_code).decode()
        info = code.split("&",5)
        print(info)
        if len(info) !=5:
            return False, None
        keys=["uri","hr","asset_type","count","comments"]
        result = dict(zip(keys, info))
        return True, json.dumps(result)

    def create_hr(self):
        key = Random.get_random_bytes(32)
        key_string = binascii.b2a_hex(key).decode()
        hr = hash_r(key_string)
        self.HashR[hr] = (key_string, self.remark)
        return hr

    @staticmethod
    def verify_hr(hr,r):
        return True if hash_r(r) == hr else False

    def fetch_r(self, hr):
        return self.HashR.get(hr)

    def delete_hr(self, hr):
        return self.HashR.pop(hr)

    @staticmethod
    def update_hash_history(hr, channel, count, state):
        LOG.debug("update hash history {}".format(channel))
        Payment.HashHistory[hr] = {"Channel":channel,
                                   "Count":count,
                                "State":state}
        return None

    @staticmethod
    def get_hash_history(hr, state="pending"):
        channel = Payment.HashHistory.get(hr)
        if not channel:
            LOG.debug("not get the channel {}/{}".format(json.dumps(Payment.HashHistory),hr))
            return None
        if channel.get("State") == state:
            return channel
        else:
            return None


def hash_r(r):
    return hashlib.sha1(r.encode()).hexdigest()

if __name__ == "__main__":
    result = Payment.decode_payment_code("TN2BfTsKzBqXChJcPrRLod7FwBy5PmwKvsiBuWuxpFGk7BSHS5Eh5HQGMoFSAAordz"
                                         "UYo9KbV8DsrrirpUnpND6RB2Yr1Z8h48CHyCNDo8zYwJPcwHRTBQzi3ARB2sZqRhsC"
                                         "HHTm3AkHAyGTt9dUgJz4y8Mej8fmUj81hk1n15LQwcF4Fqo1TY1C1cJABYu14E4biv"
                                         "GKyemF8kKYqoLiB5x3qThE221Fjhc858Chk7SgqUeJyvaFqMU")

    print(result)
    key = Random.get_random_bytes(32)
    key_string = binascii.b2a_hex(key).decode()
    print(key_string)
    print(len(key_string))


