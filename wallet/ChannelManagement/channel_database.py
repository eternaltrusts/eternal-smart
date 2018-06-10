
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

from wallet.configure import Configure
import requests
import uuid




#DATABASE_URL = Configure["DataBase"].get("url")

class DatabaseApi(object):
    """
    database api
    """

    def __init__(self, url, rcpversion="2.0"):
        self.url = url
        self.version = rcpversion

    def post_request(self, payload):
        result = requests.post(self.url, json=payload)
        if result.status_code != requests.codes.ok:
            raise result.raise_for_status()
        else:
            result.json()

    def generate_payload(self, method, params, id=None):
        id  = id if id else uuid.uuid1()
        payload = {
            "jsonrpc": self.version,
            "method": method,
            "params": params,
            "id": id
        }
        return payload

    def add_channel(self, channel, src_addr, dest_addr,
                    balance, state, alive_block, deposit, **kwargs):
        payload = {
                        "channel":channel,
                        "src_addr":src_addr,
                        "dest_addr":dest_addr,
                        "balance": balance,
                        "state":state,
                        "alive_block":alive_block,
                         "deposit":deposit
        }
        for ikey, ivalue in kwargs.items():
            payload.setdefault(ikey, ivalue)

        return self.post_request(self.generate_payload("AddChannel",payload))

    def delete_channel(self, filters):
        payload = {"filters":filters}
        return self.post_request(self.generate_payload("DeleteChannel", payload))

    def update_channel(self, filters, **kwargs):
        payload = {"filters":filters}
        for ikey, ivalue in kwargs.items():
            payload.setdefault(ikey, ivalue)
        return self.post_request(self.generate_payload("UpdateChannel", payload))

    def query_channel(self, filters, **kwargs ):
        payload = {"filters": filters}
        for ikey, ivalue in kwargs.items():
            payload.setdefault(ikey, ivalue)
        return self.post_request(self.generate_payload("QueryChannel", payload))

    def query_address (self, filters , query_all= False, **kwargs):
        payload = {"filters": filters,
                   "query_all":query_all}
        for ikey, ivalue in kwargs.items():
            payload.setdefault(ikey, ivalue)
        return self.post_request(self.generate_payload("QueryAddress", payload))



#DataBaseServer = DatabaseApi(DATABASE_URL)




