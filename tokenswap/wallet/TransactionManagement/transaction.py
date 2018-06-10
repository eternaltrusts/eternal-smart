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

#from wallet.ChannelManagement.channel import Channel
#from neo.Wallets.Wallet import Wallet

from neocore.Cryptography.Crypto import Crypto
import os
import pickle
from TX.interface import *
from wallet.utils import sign, get_asset_type_id
from wallet.BlockChain import interface as Binterface
from log import LOG
import json
from TX.utils import pubkeyToAddress

BlockHightRegister=[]
TxIDRegister= []


TxDataDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"txdata")
if not os.path.exists(TxDataDir):
    os.makedirs(TxDataDir)


class TrinityTransaction(object):

    def __init__(self, channel, wallet):
        self.channel = channel
        self.wallet = wallet
        self.tx_file = self.get_transaction_file()

    def transaction_exist(self):
        return os.path.isfile(self.tx_file)

    def signature(self, rawdata):
        return self.wallet.Sign(rawdata)

    def create_tx_file(self,channel_name):
        os.mknod(os.path.join(TxDataDir, channel_name+".data"))
        self.tx_file = self.get_transaction_file()

    def get_transaction_file(self):

         return os.path.join(TxDataDir, self.channel+".data")

    def store_transaction(self, tx_message):
        with open(self.tx_file, "wb+") as f:
            crypto_channel(f, **tx_message)
        return None

    def read_transaction(self):
        with open(self.tx_file, "rb") as f:
            try:
               return uncryto_channel(f)
            except:
                return None

    def get_role_index(self, tx_nonce):
        tx = self.get_tx_nonce(tx_nonce)
        if tx:
            role_index = tx.get("RoleIndex")
            if role_index:
                return role_index
        return None

    def update_transaction(self, tx_nonce, **kwargs):
        tx_infos = self.read_transaction()
        if tx_infos:
            info = tx_infos.get(tx_nonce)
            if not info:
                tx_infos[tx_nonce] = kwargs
            else:
                dictMerged = dict(info, **kwargs)
                tx_infos[tx_nonce] = dictMerged
        else:
            tx_infos=dict([(tx_nonce, kwargs)])
        self.store_transaction(tx_infos)

    @staticmethod
    def sendrawtransaction(raw_data):
        LOG.info("SendRawTransaction: {}".format(raw_data))
        result = Binterface.send_raw(raw_data)
        LOG.info("SendRawTransaction Result: {}".format(result))
        return result

    @staticmethod
    def genarate_raw_data(Singtxdata,Witness):
        return Singtxdata+Witness

    def get_founder(self):
        tx = self.read_transaction()
        return tx["0"]["Founder"]

    def get_balance(self, tx_nonce):
        tx = self.get_tx_nonce(tx_nonce)
        try:
            return tx["Balance"]
        except KeyError:
            return None

    def get_tx_nonce(self, tx_nonce):
        tx = self.read_transaction()
        return tx.get(tx_nonce) if tx else None

    def get_latest_nonceid(self, tx=None):
        tx = tx if tx else self.read_transaction()
        if tx is None:
            return 0
        nonce = []
        for i in tx.keys():
            try:
                if tx[i].get("State") == "confirm":
                    nonce.append(int(i))
                else:
                    continue
            except ValueError:
                continue
        return max(nonce) if nonce else 0

    def get_transaction_state(self):
        tx = self.read_transaction()
        if tx:
            return tx.get("State")
        else:
            return None

    def release_transaction(self):
        LOG.debug("release_transaction {}".format(self.channel))
        tx = self.read_transaction()
        tx_state = tx.get("State")
        if tx_state !="confirm":
            return False, "transaction state not be confirmed"
        latest_nonce =self.get_latest_nonceid(tx)
        latest_tx = tx.get(str(latest_nonce))
        LOG.debug("Latest Tx {}".format(json.dumps(latest_tx, indent=1)))
        latest_ctx = latest_tx.get("Commitment")
        ctx_txData = latest_ctx.get("originalData").get("txData")
        tx_id = latest_ctx.get("originalData").get("txId")
        ctx_witness = latest_ctx.get("originalData").get("witness")
        ctx_txData_other = latest_ctx.get("txDataSing")
        ctx_txData_sign = sign(ctx_txData, self.wallet)
        raw_data = ctx_txData+ctx_witness.format(signSelf=ctx_txData_other, signOther = ctx_txData_sign)
        result = TrinityTransaction.sendrawtransaction(raw_data)

        print("Commitment Tx to Chain    ", tx_id)
        return result


def dic2byte(file_handler, **kwargs):
    """

    :param kwargs:
    :return:
    """
    return pickle.dump(kwargs, file_handler)


def crypto_channel(file_handler, **kwargs):
    """
    :param kwargs:
    :return:
    """
    return pickle.dump(kwargs, file_handler)

def uncryto_channel(file_handler):
    """

    :param file_handler:
    :return:
    """
    return pickle.load(file_handler)

def byte2dic(file_hander):
    """

    :param file_hander:
    :return:
    """
    try:
        pickle.load(file_hander)
    except:
        return None

def pickle_load(file):
    """

    :param file:
    :return:
    """
    pickles = []
    while True:
        try:
            pickles.append(pickle.load(file))
        except EOFError:
            return pickles[0] if pickles else None

def scriptToAddress(script):
    scriptHash=Crypto.ToScriptHash(script)
    address=Crypto.ToAddress(scriptHash)
    return address


def funder_trans(params):
    """

    :param params:
    :return:
    """
    if 6 > len(params):
        LOG.error('funder_trans: Invalid params {}!'.format(params))
        return None

    selfpubkey = params[0]
    otherpubkey = params[1]
    addressFunding = params[2]
    scriptFunding = params[3]
    deposit = params[4]
    asset_type = params[6]
    founding_txid = params[5]
    asset_id = get_asset_type_id(asset_type)
    C_tx = createCTX(addressFunding=addressFunding, balanceSelf=deposit,
                          balanceOther=deposit, pubkeySelf=selfpubkey,
                          pubkeyOther=otherpubkey, fundingScript=scriptFunding, asset_id=asset_id,fundingTxId=founding_txid)

    RD_tx = createRDTX(addressRSMC=C_tx["addressRSMC"], addressSelf=pubkeyToAddress(selfpubkey),
                            balanceSelf=deposit, CTxId=C_tx["txId"],
                            RSMCScript=C_tx["scriptRSMC"], asset_id=asset_id)

    return {"C_TX":C_tx,"R_TX":RD_tx}


def funder_create(params):
        if 4 > len(params):
            LOG.error('founder_create: Invalid params {}'.format(params))
            return None

        walletfounder = {
            "pubkey":params[0],
            "deposit":float(params[2])
        }
        walletpartner = {
            "pubkey":params[1],
            "deposit":float(params[2])
        }
        asset_id = get_asset_type_id(params[3])
        founder = createFundingTx(walletpartner, walletfounder, asset_id)
        commitment = createCTX(founder.get("addressFunding"), float(params[2]), float(params[2]), params[0],
                               params[1], founder.get("scriptFunding"), asset_id, founder.get('txId'))
        address_self = pubkeyToAddress(params[0])
        revocabledelivery = createRDTX(commitment.get("addressRSMC"),address_self, float(params[2]), commitment.get("txId"),
                                       commitment.get("scriptRSMC"), asset_id)
        return {"Founder":founder,"C_TX":commitment,"R_TX":revocabledelivery}

def rsmc_trans(params):
    """

    :param params:
    :return:
    """
    if 5 > len(params):
        LOG.error('funder_trans: Invalid params {}!'.format(params))
        return None

    script_funding = params[0]
    balanceself = params[1]
    balanceother = params[2]
    pubkeyself = params[3]
    pubkeyother = params[4]
    founding_txid = params[5]
    asset_id = get_asset_type_id(params[6])

    C_tx = createCTX(addressFunding=scriptToAddress(script_funding), balanceSelf=balanceself,
                          balanceOther=balanceother, pubkeySelf=pubkeyself,
                          pubkeyOther=pubkeyother, fundingScript=script_funding, asset_id=asset_id,
                     founding_txid=founding_txid)

    RD_tx = createRDTX(addressRSMC=C_tx["addressRSMC"], addressSelf=pubkeyToAddress(pubkeyself),
                            balanceSelf=balanceself, CTxId=C_tx["txId"],
                            RSMCScript=C_tx["scriptRSMC"], asset_id=asset_id)

    return {"C_TX": C_tx, "R_TX": RD_tx}


def br_trans(params):
    """

    :param params:
    :return:
    """
    if 4 > len(params):
        LOG.error('br_trans: Invalid params {}!'.format(params))
        return None

    script_rsmc = params[0]
    selfpubkey = params[1]
    balanceself = params[2]
    ctx_id = params[3]
    asset_id = get_asset_type_id(params[4])

    BR_tx = createBRTX(addressRSMC=scriptToAddress(script_rsmc), addressOther=pubkeyToAddress(selfpubkey),
                            balanceSelf=balanceself, RSMCScript=script_rsmc,  CTxId=ctx_id, asset_id=asset_id)

    return {"BR_tx": BR_tx}

def hltc_trans(params):
    """

    :param params:
    :return:
    """
    if 9 > len(params):
        LOG.error('hltc_trans: Invalid params {}!'.format(params))
        return None

    pubkeySender = params[0]
    pubkeyReceiver = params[1]
    HTLCValue = params[2]
    balanceSender = params[3]
    balanceReceiver = params[4]
    hashR = params[5]
    addressFunding = params[6]
    fundingScript = params[7]
    asset_id = get_asset_type_id(params[8])


    return create_sender_HTLC_TXS(pubkeySender, pubkeyReceiver, HTLCValue, balanceSender,
                                  balanceReceiver, hashR, addressFunding,
                                  fundingScript, asset_id)

def refound_trans(params):
    """

    :param params:
    :return:
    """
    addressFunding = params[0].strip()
    balanceSelf = float(params[1])
    balanceOther = float(params[2])
    pubkeySelf = params[3].strip()
    pubkeyOther = params[4].strip()
    fundingScript = params[5].strip()
    asset_id = get_asset_type_id(params[6].strip())
    return createRefundTX(addressFunding, balanceSelf, balanceOther,
                                           pubkeySelf, pubkeyOther, fundingScript, asset_id)





if __name__== "__main__":
    tx = TrinityTransaction("Mytest","walle")
    TrinityTransaction("Mytest","wallt")
    m = {"test1":1}
    m1 = {"test2":2}
    tx.update_transaction("0",test1=1)
    tx.update_transaction("0",test2=2)
    print(tx.read_transaction())
    tx.update_transaction("1",H=1,x="tt")
    print(tx.read_transaction())





