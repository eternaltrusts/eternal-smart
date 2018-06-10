# -*- coding: utf-8 -*-
__author__ = 'xu'
import bcrypt
import random
import requests
from decimal import Decimal, getcontext
from datetime import datetime, date, timedelta
from functools import wraps
from math import ceil
from flask import jsonify, g, abort,request, url_for,redirect
# from flask_security import current_user, login_user
from models import Order, SendTransactions, MonitorTransactions
from . import auth,db,app
import types

def create_tables():
    auth.User.create_table(fail_silently=True)
    # Users.create_table(fail_silently=True)
    # Role.create_table(fail_silently=True)
    # UserRoles.create_table(fail_silently=True)
    Order.create_table(fail_silently=True)
    SendTransactions.create_table(fail_silently=True)
    MonitorTransactions.create_table(fail_silently=True)
    
def make_data(code=0, data=None, error=None):
    data = {
        "Code": code,
        "Error": "" if not error else error,
        "Data": data
    }
    return jsonify(data)

class Pagination(object):
    def __init__(self, cur_page, per_page, total_count):
        self.cur_page = cur_page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.cur_page > 1

    @property
    def has_next(self):
        return self.cur_page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        has_gen_none = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (self.cur_page - left_current - 1 < num < self.cur_page + right_current):
                yield num
            elif not has_gen_none:
                yield None
                has_gen_none = 1

def url_for_page(page, arg=None):
    args = request.args.copy()
    args['page'] = page
    if request.endpoint == 'product_cate':
        return url_for(request.endpoint, cid=arg, **args)
    else:
        return url_for(request.endpoint, **args)

def url_for_search(key,value):
    args = request.args.copy()
    args[key] = value
    if not value:
        del args[key]
    
    return url_for(request.endpoint, **args)

def current_user_has_role(role_name):
    """
    验证当前用户是否拥有某个角色
    """
    return current_user.has_role(role_name)

def request_data_to_dict():
    """
    请求数转dict
    """
    data = {}
    if request.is_json:
        data = request.json
    elif len(request.form.keys()):
        for key in request.form.keys():
            if len(key) > app.config["FORM_KEY_LEN"]: abort(400)
            tmp = key if not key.endswith("[]") else key[:-2]
            if len(request.form.getlist(key)) > 1:
                data[tmp] = request.form.getlist(key)
            else:
                data[tmp] = request.form.getlist(key)[0]
    return data

def create_verify_code():
    """
    生成6位随机数字验证码
    """
    code = random.randint(100000,999999)
    return str(code)

def make_order_amount(value, now_time=None, swap_conf=None):
    if not swap_conf:
        swap_conf = app.config["TOKEN_SWAP_CONF"]
    de_tax = Decimal(swap_conf["tax"])
    # rand_str = str(random.randint(1000, 9999))
    # time_str = now_time.strftime("%f")[:4]
    # de_float = Decimal("0.{}{}".format(rand_str, time_str))
    de_value = Decimal(value)
    # send_amount = (de_value + de_float).quantize(Decimal("0.00000000"))
    send_amount = de_value.quantize(Decimal("0.00000000"))
    tax_cost = (de_tax * send_amount).quantize(Decimal("0.00000000"))
    rev_amount = (send_amount - tax_cost).quantize(Decimal("0.00000000"))
    print(send_amount, rev_amount, tax_cost)
    return str(send_amount), str(rev_amount), str(tax_cost)

def fixed_8float_str(value):
    de_value = Decimal(value).quantize(Decimal("0.00000000"))
    return str(de_value)

def request_transactions(addr_from, addr_to, value, asset_type):
    """
    request transactions\n
    :param asset_type: the type of request transactions: neo or eth
    """
    request_url = app.config["NEO_VERIFY_URL"] if asset_type == types.asset_type["neo"] else app.config["ETH_VERIFY_URL"]
    api_verify = app.config["API_VERIFY"]
    verify_header_name = api_verify["verify_header"]
    verify_header_value = api_verify["password"]
    print request_url
    try:
        res = requests.post(
            request_url,
            headers = {
                verify_header_name: verify_header_value
            },
            json = {
                "jsonrpc": "2.0",
                "method": "autoTransferTNC",
                # "params": ["AGgZna4kbTXPm16yYZyG6RyrQz2Sqotno6","AN1AUtxuHHB6MASpV1yEyABaEfTDBGGh9o",1.25645645],
                "params": [addr_to, value],
                "id": 1
            }
        )
        print res.json()
        result = res.json().get("result")
    except Exception:
        result = None
    return result

def hash_password(password):
    """
    使用 CRYPT_BLOWFISH 算法创建散列\n
    随机 salt 保存在密码 hashed 中
    """
    if isinstance(password, unicode):
        password = password.encode("utf-8")
    try:
        salt = salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password, salt)
    except Exception:
        hashed = None
    return hashed

def verify_password(password, hashed):
    if isinstance(password, unicode):
        password = password.encode("utf-8")
    if isinstance(hashed, unicode):
        hashed = hashed.encode("utf-8")
    print(password, hashed)
    try:
        result = bcrypt.checkpw(password, hashed)
    except Exception:
        result = False
    return result

def api_verify(f):
    """
    api verify decorated_function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_verify = app.config["API_VERIFY"]
        verify_header_name = api_verify["verify_header"]
        print(verify_header_name)
        hashed = api_verify["hashed"]
        password = request.headers.get(verify_header_name, "")
        if not verify_password(password, hashed):
            return make_data(code=1, error="api verify failed!")
        return f(*args, **kwargs)
    return decorated_function

def verify_tx_type(sender, receiver):
    """
    return :(asset_type:1/2, tx_type:1/2)
    """
    token_swap_conf = app.config["TOKEN_SWAP_CONF"]
    neo_addr = token_swap_conf["neo_addr"]
    eth_addr = token_swap_conf["eth_addr"]
    tx_type = "in_tx" if receiver in [neo_addr, eth_addr] else "out_tx"
    asset_type = "neo" if neo_addr in [sender, receiver] else "eth"
    print tx_type, asset_type
    return types.asset_type[asset_type], types.tx_type[tx_type]

def select_local_send_addr(rev_asset_type):
    token_swap_conf = app.config["TOKEN_SWAP_CONF"]
    neo_addr = token_swap_conf["neo_addr"]
    eth_addr = token_swap_conf["eth_addr"]
    if rev_asset_type == types.asset_type["neo"]: return eth_addr
    else: return neo_addr
    