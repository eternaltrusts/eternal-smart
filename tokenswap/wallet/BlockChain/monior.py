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


from log import LOG
#from neo.Core.Blockchain import Blockchain
import time
from wallet.TransactionManagement.transaction import BlockHightRegister, TxIDRegister,TxDataDir, crypto_channel
import os
from wallet.Interface.gate_way import send_message
import copy
from .interface import get_block_count, get_bolck, send_raw
from wallet.TransactionManagement import message as ms

BlockHeightRecord = os.path.join(TxDataDir,"block.data")


class Monitor(object):
    GoOn = True
    Wallet = None
    Wallet_Change = None
    BlockHeight = None
    BlockPause = False

    @classmethod
    def stop_monitor(cls):
        cls.GoOn = False

    @classmethod
    def start_monitor(cls, wallet):
        cls.Wallet = wallet
        cls.Wallet_Change = True

    @classmethod
    def update_wallet_block_height(cls, blockheight):
        if cls.Wallet_Change:
            return None
        if cls.Wallet:
            cls.Wallet.BlockHeight=blockheight
        else:
            #LOG.debug("Wallet not opened")
            return None

    @classmethod
    def get_wallet_block_height(cls):
        if cls.Wallet:
            block_height = cls.Wallet.BlockHeight
            cls.Wallet_Change = False
            return block_height if block_height else 1
        else:
            #LOG.debug("Wallet not opened")
            return 1

    @classmethod
    def update_block_height(cls, blockheight):
        cls.BlockHeight = blockheight

    @classmethod
    def get_block_height(cls):
        return cls.BlockHeight if cls.BlockHeight else 1


def monitorblock():
    while Monitor.GoOn:
        blockheight_onchain = get_block_count()
        Monitor.update_block_height(blockheight_onchain)

        blockheight = Monitor.get_wallet_block_height()

        block_delta = int(blockheight_onchain) - int(blockheight)

        if blockheight:
            try:
                if block_delta < 2000:
                    block = get_bolck(int(blockheight))
                    handle_message(int(blockheight),block)
                    if Monitor.BlockPause:
                        pass
                    else:
                        blockheight += 1
                else:
                    blockheight +=1000
                    pass
                Monitor.update_wallet_block_height(blockheight)
            except Exception as e:
                pass
        else:
            #LOG.debug("Not get the blockheight")
            pass

        if blockheight < blockheight_onchain:
            #time.sleep(0.1)
            pass
        else:
            time.sleep(15)


def send_message_to_gateway(message):
    send_message(message)


def handle_message(height,jsn):
    match_list=[]
    block_txids = [i.get("txid") for i in jsn.get("tx")]
    blockheight = copy.deepcopy(BlockHeightRecord)
    ms.SyncBlockMessage.send_block_sync(Monitor.Wallet,blockheight,block_txids)
    for index,value in enumerate(blockheight):
        if value[0] == height:
            value[1](*value[1:])
            match_list.append(value)
    for i in match_list:
        BlockHightRegister.remove(i)
    match_list =[]
    txids = copy.deepcopy(TxIDRegister)
    for value in txids:
        txid = value[0]
        LOG.info("Handle Txid: {}".format(txid))
        if txid in block_txids:
            value[1](value[0],*value[2:])
            match_list.append(value)
        else:
            continue
    for i in match_list:
        TxIDRegister.remove(i)
    return



def register_monitor(*args):
    TxIDRegister.append(args)


def register_block(*args):
    BlockHightRegister.append(args)


def record_block(txid, block_height):
    with open(BlockHeightRecord, "wb+") as f:
        info = {}
        info.setdefault(txid, block_height)
        crypto_channel(f,**info)



if __name__  == "__main__":
   blockcount = get_block_count()
   print(get_bolck(int(blockcount)-1))

   raw="d101a00400ca9a3b14f5db0e4427fbf90d1fa21c741545b3fd0a12e68314d31081412" \
       "47338aa337da861b31ee214ce460fec53c1087472616e73666572675e7fb71d90044445" \
       "caf77c0c36df0901fda8340cf10400ca9a3b14f5db0e4427fbf90d1fa21c741545b3fd0a" \
       "12e6831487cc4b925bd8f6f3c4a77a20382af79c7d7c0b0753c1087472616e7366657267" \
       "5e7fb71d90044445caf77c0c36df0901fda8340cf100000000000000000320d310814124" \
       "7338aa337da861b31ee214ce460fec2087cc4b925bd8f6f3c4a77a20382af79c7d7c0b07f" \
       "0045ac2017a000002414038a00c590ebe049874bde93cf78e033054319a09b6d4909ecb44c2" \
       "e23231bdda0ef462729a1c167e5155344520a97dbd4ba2f45f0d38eaadc9c6c515aef8ff732" \
       "321034531bfb4a0d5ed522d9d6bcb4243c8e15cb1ad04d76531a204e5e79784aa3719ac4140" \
       "daa4014f199663f2f3d0f662e042ac9ff4ded09269d7e8b3978a75fdd4d8172508218a2c5a3" \
       "8072b48716eb8d32cb67c43cdd65750dabab7ea3a4775eee114582321022369f2ed62f20b90a6" \
       "1053d26b8628cca4d4b267b8ac1f3cbc51e4d308711ae8ac"
   print(send_raw(raw))








