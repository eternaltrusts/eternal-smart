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


from neocore.Cryptography.Crypto import Crypto
import binascii
from wallet.configure import Configure
from wallet.BlockChain.interface import get_balance
import re
import hashlib
from log import LOG
import requests
import datetime

SupportAssetType = ["TNC", "NEO", "GAS"] #Todo multi-asset will come soon, before that hardcode here


class DepositAuth(object):
    DefaultDeposit = 5000
    LastGetTime = None
    DateSource = "https://api.coinmarketcap.com/v2/ticker/2443/?convert=USD"

    @classmethod
    def query_depoist(cls):
        try:
            result = requests.get(cls.DateSource)
            if not result.ok:
                return None
            return result.json()["data"]
        except Exception as e:
            LOG.error(str(e))
            return None

    @classmethod
    def caculate_depoistusd(cls):
        return 800*1.03**(abs((datetime.date.today()-datetime.date(2018,1,15)).days)//365)

    @classmethod
    def caculate_depoist(cls):
        depoist_info = cls.query_depoist()
        try:
            tnc_price_usdt = depoist_info["quotes"]["USD"]["price"]
            depoist_limit = int(cls.caculate_depoistusd()/tnc_price_usdt)
            return depoist_limit if depoist_limit >0 else 1
        except Exception as e:
            LOG.error(str(e))
            return cls.DefaultDeposit


    @classmethod
    def deposit_limit(cls):
        # if not cls.LastGetTime or datetime.date.today() != cls.LastGetTime:
        deposit = cls.caculate_depoist()
        cls.DefaultDeposit = deposit
        cls.LastGetTime = datetime.date.today()

        return cls.DefaultDeposit


def to_aes_key(password):
    """

    :param password:
    :return:
    """

    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    return hashlib.sha256(password_hash).digest()


def pubkey_to_address(publickey: str):
    """

    :param publickey:
    :return:
    """
    script = b'21' + publickey.encode() + b'ac'
    script_hash = Crypto.ToScriptHash(script)
    address = Crypto.ToAddress(script_hash)
    return address


def sign(wallet, context):
    """

    :param wallet:
    :param context:
    :return:
    """
    res = wallet.SignContent(context)
    return res

def get_arg(arguments, index=0, convert_to_int=False):
    """

    :param arguments:
    :param index:
    :param convert_to_int:
    :param do_parse:
    :return:
    """

    try:
        arg = arguments[index]
        if convert_to_int:
            return int(arg)
        return arg
    except Exception as e:
        pass
    return None


def get_asset_type_name(asset_type):
    """

    :param asset_type:
    :return:
    """
    asset= Configure.get("AssetType")
    for key, value in asset.items():
        if value.replace("0x","") == asset_type.replace("0x",""):
            return key.upper()
        else:
            continue
    return None


def get_asset_type_id(asset_name):
    """

    :param asset_name:
    :return:
    """

    if len(asset_name) > 10:
        return asset_name
    else:
        return Configure.get("AssetType").get(asset_name.upper())


def check_support_asset_type(asset_type):
    """

    :param asset_type:
    :return:
    """
    if asset_type.upper() in SupportAssetType:
        return True
    else:
        return False


def check_onchain_balance(pubkey,asset_type,depoist):
    """

    :param wallet:
    :param asset_type: eg TNC
    :param depoist:
    :return:
    """
    balance = get_balance(pubkey, asset_type)
    if 0 < float(depoist) <= float(balance):
        return True
    else:
        return False


def check_max_deposit(deposit):
    maxd = Configure.get("CommitMaxDeposit")
    if maxd is None or str(maxd).upper() == "NULL":
        return True, None
    else:
        try:
            maxd = float(maxd)
        except ValueError as e:
            return False, str(e)

        return float(deposit) <= maxd, maxd


def check_min_deposit(deposit):
    mixd = Configure.get("CommitMinDeposit")
    if mixd is None or float(mixd) == 0:
        return True, None
    else:
        try:
            mixd = float(mixd)
        except ValueError as e:
            return False, str(e)
        return float(deposit) >= mixd, mixd


def check_deposit(deposit):
    try:
        de = float(deposit)
    except ValueError as e:
        return False, str(e)
    return de > 0, de


def convert_to_float(deposit):
    try:
        return float(deposit)
    except Exception as error:
        return 0


def convert_number_auto(asset_type, number: int or float or str):
    if asset_type in ['NEO']:
        LOG.warning('Convert number<{}> to integer for asset<{}> just support integer type transaction.'.format(number, asset_type))
        if isinstance(number, str):
            number = float(number)
        return int(number)

    return number


def is_supported_value_type(asset_type, value: float or int):
    if isinstance(value, int):
        return True
    else:
        decimal_part = str(value).split('.')[1].strip()
        if asset_type in ['NEO'] and 0 != int(decimal_part):
            return False

        return True


def is_valid_deposit(asset_type, deposit, spv_wallet=False):
    """

    :param asset_type:
    :param deposit:
    :param spv_wallet:
    :return:
    """
    if len(asset_type) >10:
        asset_type = get_asset_type_name(asset_type)
    else:
        asset_type = asset_type.upper()

    if not asset_type:
        LOG.error('Must specified the asset type. Current value is None')
        return False

    if not is_supported_value_type(asset_type, deposit):
        LOG.error('Invalid Type. Unsupported value<{}> for asset<{}>.'.format(deposit, asset_type))
        return False

    if spv_wallet:
        try:
            max_deposit_configure = Configure.get("Channel").get(asset_type).get("CommitMaxDeposit")
        except Exception as e:
            LOG.warn(str(e))
            max_deposit_configure = 0
        try:
            min_deposit_configure = Configure.get("Channel").get(asset_type.upper()).get("CommitMinDeposit")
        except Exception as e:
            LOG.warn(str(e))
            min_deposit_configure = 0

        max_deposit = convert_to_float(max_deposit_configure)
        min_deposit = convert_to_float(min_deposit_configure)

        if min_deposit > 0 and max_deposit > 0:
            return min_deposit <= deposit <= max_deposit, None

        elif 0 >= min_deposit:
            LOG.warn('CommitMinDeposit is set as an illegal value<{}>.'.format(str(min_deposit)))
            return deposit <= max_deposit, None
        elif 0 >= max_deposit:
            LOG.warn('CommitMaxDeposit is set as an illegal value<{}>.'.format(str(max_deposit)))
            return deposit >= min_deposit, None
    else:
        if asset_type == "TNC":
            deposit_l = DepositAuth.deposit_limit()
            if deposit <= deposit_l:
                return False, "Node wallet channel deposit should larger than {}, " \
                              "but now is {}".format(str(deposit_l),str(deposit))
        return True, None


def check_partner(wallet, partner):
    """

    :param wallet:
    :param partner:
    :return:
    """
    p = re.match(r"[0-9|a-f]{66}@\d+\.\d+\.\d+\.\d+:\d+", partner.strip())
    if p:
        par_pubkey, ip = partner.strip().split("@")
        if par_pubkey == wallet.pubkey:
            return False
        else:
            return True
    else:
        return False



def get_wallet_info(pubkey):
    """

    :param pubkey:
    :return: message dict
    """
    balance = {}
    for i in Configure["AssetType"].keys():
        b = get_balance(pubkey, i.upper())
        balance[i] = b
    message = {
                   "Publickey": pubkey,
                    "alias": Configure["alias"],
                    "AutoCreate": Configure["AutoCreate"],
                    "Ip": "{}:{}".format(Configure.get("NetAddress"),
                                         Configure.get("NetPort")),
                    "MaxChannel": Configure["MaxChannel"],
                   "Channel": Configure["Channel"],
                   "Balance": balance,
               }
    return message


if __name__ == "__main__":
    import time
    while True:
        print(DepositAuth.deposit_limit())