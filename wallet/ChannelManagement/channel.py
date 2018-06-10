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
import hashlib
import time
from model.channel_model import APIChannel
from model.base_enum import EnumChannelState
from wallet.TransactionManagement import message as mg
from wallet.utils import pubkey_to_address, convert_number_auto
from wallet.Interface.gate_way import sync_channel
from log import LOG
import json


class Channel(object):
    """

    """
    def __init__(self,founder, partner):
        self.founder = founder
        self.partner = partner
        self.founder_pubkey = self.founder.split("@")[0]
        self.founder_address = pubkey_to_address(self.founder_pubkey)
        self.partner_pubkey = self.partner.split("@")[0]
        self.partner_address = pubkey_to_address(self.partner_pubkey)


    @staticmethod
    def get_channel(address1, address2, state):
        channels = []
        channel = APIChannel.batch_query_channel(filters={"src_addr": address1, "dest_addr": address2,"state":state })
        if channel.get("content"):
            channels.extend(channel["content"])

        channel= APIChannel.batch_query_channel(filters={"src_addr":address2, "dest_addr":address1, "state":state})
        if channel.get("content"):
            channels.extend(channel["content"])

        return channels

    @staticmethod
    def query_channel(address):
        print("Get Channels with Address %s" %address)
        channels = APIChannel.batch_query_channel(filters={"src_addr":address})
        if channels.get("content"):
            for ch in channels["content"]:
                print("=="*10,"\nChannelName:", ch.channel, "\nState:", ch.state, "\nPeer:", ch.dest_addr,
                      "\nBalance:", json.dumps(ch.balance, indent=1))
        channeld = APIChannel.batch_query_channel(filters={"dest_addr":address})
        if channeld.get("content"):
            for ch in channeld["content"]:
                print("=="*10,"\nChannelName:", ch.channel, "\nState:", ch.state, "\nPeer:", ch.src_addr,
                      "\nBalance:", json.dumps(ch.balance, indent=1))


    @classmethod
    def channel(cls,channelname):
        try:
            channel = APIChannel.query_channel(channel=channelname)
            channel_info = channel["content"][0]
        except Exception as e:
            return None
        ch =cls(channel_info.src_addr, channel_info.dest_addr)
        ch.channel_name = channelname
        ch.channel_info = channel_info
        return ch


    def _init_channle_name(self):
        md5s = hashlib.md5(self.founder.encode())
        md5s.update(self.partner.encode())
        md5s.update(str(time.time()).encode())
        return md5s.hexdigest().upper()

    def create(self, asset_type, deposit, cli=True, comments= None, channel_name = None):
        #if Channel.get_channel(self.founder_pubkey, self.partner_pubkey):
            #raise ChannelExist
        self.start_time = time.time()
        self.asset_type = asset_type
        self.deposit = {}
        subitem = {}
        subitem.setdefault(asset_type, deposit)
        self.deposit[self.founder_pubkey] = subitem
        self.deposit[self.partner_pubkey] = subitem
        self.channel_name = self._init_channle_name() if not channel_name else channel_name
        print(self.channel_name)

        result = APIChannel.add_channel(self.channel_name,self.founder, self.partner,
                     EnumChannelState.INIT.name, 0, self.deposit)
        if cli:
            deposit = convert_number_auto(asset_type.upper(), deposit)
            if 0 >= deposit:
                LOG.error('Could not trigger register channel because of illegal deposit<{}>.'.format(deposit))
                return False

            message={"MessageType":"RegisterChannel",
                 "Sender": self.founder,
                 "Receiver": self.partner,
                 "ChannelName": self.channel_name,
                 "MessageBody":{
                                "AssetType":asset_type,
                                "Deposit":deposit,
                                "Comments":comments
                                }
            }
            return mg.Message.send(message)

        return result

    def delete(self):
        pass

    def update_channel(self, **kwargs):
        return APIChannel.update_channel(self.channel_name, **kwargs)

    def delete_channel(self):
        return APIChannel.delete_channel(self.channel_name)

    @property
    def state(self):
        return None

    @property
    def src_addr(self):
        ch = self._get_channel()
        if ch:
            return ch.src_addr
        else:
            return None

    @property
    def dest_addr(self):
        ch = self._get_channel()
        if ch:
            return ch.dest_addr
        else:
            return None

    def _get_channel(self):
        try:
            channel = APIChannel.query_channel(self.channel_name)
            return channel["content"][0]
        except Exception as e:
            LOG.error(e)
            return None

    def get_balance(self):
        ch = self._get_channel()
        if ch:
            return ch.balance
        else:
            return None

    def get_peer(self, url):
        if self.founder == url:
            return self.partner
        elif self.partner == url:
            return self.founder
        else:
            return None

    def get_deposit(self):
        ch = self._get_channel()
        if ch:
            return ch.deposit
        else:
            return None

    def toJson(self):
        jsn = {"ChannelName":self.channel_name,
               "Founder":self.founder,
               "Parterner":self.partner,
               "State":self.state,
               "Deposit":self.get_deposit(),
               "Balance":self.get_balance()}
        return jsn

    def get_role_in_channel(self, url):
        if url == self.src_addr:
            return "Founder"
        elif url == self.dest_addr:
            return "Partner"
        else:
            return None



def create_channel(founder, partner, asset_type, depoist:float, cli=True, comments = None, channel_name = None):
    return Channel(founder, partner).create(asset_type, depoist, cli, comments, channel_name)


def filter_channel_via_address(address1, address2, state=None):
    channel = Channel.get_channel(address1, address2, state)
    return channel


def get_channel_via_address(address):
    Channel.query_channel(address)
    return


def get_channel_via_name(params):
    print ('enter get_channel_via_name', params)
    if params:
        print('params is ', params)
        channel_set = APIChannel.batch_query_channel(filters=params[0]).get('content')
        print('channel_set is ', channel_set)
        result=[]
        for channel in channel_set:
            result.append({k:v for k, v in channel.__dict__.items() if k in APIChannel.table.required_item})
        print('result is ', result)
        return result
    return None


def chose_channel(channels, publick_key, tx_count, asset_type):
    for ch in channels:
        balance = ch.balance
        LOG.debug("balance {}".format(balance))
        if balance:
            try:
                balance_value = balance.get(publick_key).get(asset_type.upper())
                # Currently, each channel just is mapping to one asset type, so check the balance_value is needed
                if not balance_value:
                    continue
            except:
                continue
            if float(balance_value) >= float(tx_count):
                return ch
            else:
                continue


def close_channel(channel_name, wallet):
    ch = Channel.channel(channel_name)
    if ch:
        balance = ch.get_balance()
    else:
        LOG.error('Channel <{}> not found!'.format(channel_name))
        return

    public_key = wallet.url.split('@')[0]
    if balance and balance.get(public_key):
        asset_type = list(list(balance.values())[0].keys())[0].upper()
    else:
        LOG.error('Illegal balance<{}> of channel<{}>'.format(balance, channel_name))
        return

    peer = ch.get_peer(wallet.url)

    #tx = trans.TrinityTransaction(channel_name, wallet)
    #tx.release_transaction()
    mg.SettleMessage.create(channel_name,wallet,wallet.url, peer, asset_type) #ToDo


def sync_channel_info_to_gateway(channel_name, type):
    LOG.info("Debug sync_channel_info_to_gateway  channelname {} type {}".format(channel_name, type))
    ch = Channel.channel(channel_name)
    balance = ch.get_balance()
    nb = {}
    for item, value in balance.items():
        if item in ch.founder:
            nb[ch.founder] = value
        else:
            nb[ch.partner] = value

    return sync_channel(type, ch.channel_name,ch.founder,ch.partner,nb)


def udpate_channel_when_setup(address):
    """

    :param address: wallet url
    :return:
    """

    channels = APIChannel.batch_query_channel(filters={"src_addr":address, "state":EnumChannelState.OPENED.name})
    channel_list =[]
    if channels.get("content"):
        for ch in channels["content"]:
            c = Channel.channel(ch.channel)
            channel_info = {"ChannelName": ch.channel,
                            "Founder": ch.src_addr,
                             "Receiver": ch.dest_addr,
                             "Balance": c.get_balance()}
            channel_list.append(channel_info)
    channeld = APIChannel.batch_query_channel(filters={"dest_addr":address,"state":EnumChannelState.OPENED.name})
    if channeld.get("content"):
        for ch in channeld["content"]:
            c = Channel.channel(ch.channel)
            channel_info = {"ChannelName": ch.channel,
                            "Founder": ch.src_addr,
                            "Receiver": ch.dest_addr,
                            "Balance": c.get_balance()}
            channel_list.append(channel_info)
    return channel_list

if __name__ == "__main__":
    result = APIChannel.query_channel(channel="1BE0FCD56A27AD46C22B8EEDC4E835EA")
    print(result)
    print(dir(result["content"][0]))
    print(result["content"][0].dest_addr)
    print(result["content"][0].src_addr)

    result = APIChannel.batch_query_channel(filters={"dest_addr": "022a38720c1e4537332cd6e89548eedb0afbb93c1fdbade42c1299601eaec897f4",
                                            "src_addr":"02cebf1fbde4786f031d6aa0eaca2f5acd9627f54ff1c0510a18839946397d3633"})
    print(result)