# -*- coding: utf-8 -*-
import time
from datetime import datetime
from flask import request
# from flask_security import current_user, login_user,roles_accepted
from . import app
from utils import make_data, make_order_amount, request_transactions, \
    request_data_to_dict, api_verify, verify_tx_type, select_local_send_addr, fixed_8float_str
from models import Order, MonitorTransactions, SendTransactions, IntegrityError
import types
import logging
gunicorn_error_logger = logging.getLogger("gunicorn.error")

@app.route("/trade", methods=["POST"])
def trade():
    if request.method == "POST":
        args = request.args.copy()
        sender = args.get("from")
        receiver = args.get("to")
        value = args.get("value")
        swap_type = None
        if not sender or not receiver or not value:
            return make_data(code=1, error="invalid input")
        if sender.startswith("0x") and len(sender) == 42:
            sender = sender.lower()
            if len(receiver) != 34:
                return make_data(code=1, error="address error")
            swap_type = "eth-to-neo"
        elif receiver.startswith("0x") and len(receiver) == 42:
            receiver = receiver.lower()
            if len(sender) != 34:
                return make_data(code=1, error="address error")
            swap_type = "neo-to-eth"
        else:
            return make_data(code=1, error="address error")
        try:
            amount_float = float(value)
        except Exception:
            return make_data(code=1, error="value error")
        else:
            amount_min = app.config["TOKEN_SWAP_CONF"]["min"]
            amount_max = app.config["TOKEN_SWAP_CONF"]["max"]
            error = ""
            if amount_float > amount_max:
                error = "amount too large, max amount: ".format(amount_max)
            elif amount_float < amount_min:
                error = "amount must ove: ".format(amount_min)
            if error: return make_data(code=1, error=error)
        if Order.check_exist_unpay_order(sender):
            error = "exist uncomplete order"
            return make_data(code=1, error=error)
        neo_addr = app.config["TOKEN_SWAP_CONF"]["neo_addr"]
        eth_addr = app.config["TOKEN_SWAP_CONF"]["eth_addr"]
        swap_conf = app.config["TOKEN_SWAP_CONF"]
        now_time = datetime.now()
        send_amount, rev_amount, tax_cost = make_order_amount(value, now_time, swap_conf)
        order = Order.create_order(
            sender=sender,
            receiver=receiver,
            created_time=now_time,
            swap_type=swap_type,
            send_value=send_amount,
            receiver_value=rev_amount,
            tax_cost=tax_cost
        )
        data = {
            "Address": neo_addr if swap_type == "neo-to-eth" else eth_addr,
            "CreateTime": int(time.mktime(now_time.timetuple())),
            "TX": order.tx_no,
            "Value": send_amount
        }
        return make_data(data=data)

@app.route("/trade/<string:tx_no>")
def trade_check(tx_no):
    if not tx_no.startswith("order_no"):
        error = "trade number error"
        return make_data(code=1, error=error)
    order = Order.get_order_by_tx_no(tx_no)
    if not order:
        error = "trade number error"
        return make_data(code=1, error=error)
    else:
        data = {
            "ID": order.id,
            "TX": order.tx_no,
            "InTx": order.in_tx,
            "OutTx": order.out_tx,
            "From": order.sender,
            "To": order.receiver,
            "CreateTime": order.created_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "CompletedTime": order.rev_complete_time.strftime("%Y-%m-%dT%H:%M:%SZ") if order.rev_complete_time else None
        }
    return make_data(data=data)

@app.route("/tradeinfo")
def tradeinfo():
    if request.method == "GET":
        token_swap_conf = app.config["TOKEN_SWAP_CONF"]
        data = {
            "eth2neotax": token_swap_conf["tax"],
            "limitAmount": token_swap_conf["min"],
            "maxAmount": token_swap_conf["max"], 
            "neo2ethtax": token_swap_conf["tax"]
        }
        return make_data(data=data)

@app.route("/monitor/transactions", methods=["POST"])
@api_verify
def accept_transactions():
    # print request.remote_addr
    data = request_data_to_dict()
    sender = data.get("addressFrom")
    receiver = data.get("addressTo")
    value = data.get("value")
    tx_id = data.get("txId")
    timestamp = data.get("blockTimestamp")
    print data
    if not sender or not receiver or not tx_id:
        return make_data(code=1, error="invalid request!")
    if isinstance(timestamp, str): timestamp = float(timestamp)
    complete_time = datetime.fromtimestamp(timestamp)
    asset_type, tx_type = verify_tx_type(sender, receiver)
    try:
        MonitorTransactions.create(
            tx_id = tx_id,
            sender = sender,
            receiver = receiver,
            value = value,
            complete_time = complete_time,
            asset_type = asset_type,
            tx_type = tx_type
        )
    except IntegrityError as e:
        gunicorn_error_logger.error("IntegrityError when insert MonitorTransactions record: {}******".format(e.args))
        gunicorn_error_logger.warning("******Accept the repeat transactions: tx_id_{}******".format(tx_id))
        return make_data(code=0)
    multi_filter = list()
    transactions_conf = {"request_tx": False}
    # in_tx
    if tx_type == types.tx_type["in_tx"]:
        print fixed_8float_str(value)
        multi_filter.append(Order.send_value == fixed_8float_str(value))
        multi_filter.append(Order.sender == sender)
        multi_filter.append(Order.status == types.order_type["unpay"])
        update_order_status = "paid"
        update_orde_tx = "in_tx"
        update_order_time = "pay_complete_time"
        if sender not in app.config["TOKEN_SWAP_CONF"]["recharge_addrs"]:
            transactions_conf["request_tx"] = True
    # out_tx
    else:
        multi_filter.append(Order.receiver == receiver)
        multi_filter.append(Order.receiver_value == fixed_8float_str(value))
        multi_filter.append(Order.status == types.order_type["sent"])
        update_order_status = "completed"
        update_orde_tx = "out_tx"
        update_order_time = "rev_complete_time"
        send_transactions = SendTransactions.get_or_none(
            SendTransactions.tx_id == tx_id
        )
        print "send_transactions:", send_transactions
        if send_transactions:
            send_transactions.complete_time = complete_time
            send_transactions.status = types.send_tx_type["verified"]
            send_transactions.save()
        else:
            gunicorn_error_logger.critical("**********Detected an out_tx not sent by token_swap_system. tx_id_{}******".format(tx_id))
    order = Order.get_order_by_filter(*multi_filter)
    print multi_filter
    print "order:", order
    # matching the order
    if order:
        setattr(order, update_orde_tx, tx_id)
        setattr(order, "status", types.order_type[update_order_status])
        setattr(order, update_order_time, complete_time)
        # print order.status, order.pay_complete_time, order.in_tx
        # order.save()
        if transactions_conf["request_tx"]:
            transactions_conf["receiver"] = order.receiver
            transactions_conf["sender"] = select_local_send_addr(asset_type)
            transactions_conf["value"] = order.receiver_value
            transactions_conf["asset_type"] = types.asset_type["neo"] if asset_type == types.asset_type["eth"] else types.asset_type["eth"]
            transactions_conf["remark"] = types.send_tx_remark["order_matching"]
    # mismatching order refund origin token(need minus tax)
    elif transactions_conf["request_tx"]:
        transactions_conf["receiver"] = sender
        transactions_conf["sender"] = receiver
        transactions_conf["value"] = make_order_amount(value)[1]
        transactions_conf["asset_type"] = asset_type
        transactions_conf["remark"] = types.send_tx_remark["order_mismatching"]
    # print transactions_conf
    if transactions_conf["request_tx"]:
        result = request_transactions(
            transactions_conf["sender"],
            transactions_conf["receiver"],
            float(transactions_conf["value"]),
            transactions_conf["asset_type"]
        )
        if result and result.get("txId"):
            try:
                SendTransactions.create(
                    tx_id = result["txId"],
                    sender = transactions_conf["sender"],
                    receiver = transactions_conf["receiver"],
                    value = transactions_conf["value"],
                    remark = transactions_conf["remark"],
                    asset_type = transactions_conf["asset_type"],
                    tx_type = tx_type
                )
                if order and order.status == types.order_type["paid"]:
                    order.status = types.order_type["sent"]
            except Exception as e:
                gunicorn_error_logger.error("Error when insert SendTransactions record: {}******\n******tx_id_{}******".format(e.args, tx_id))
        else:
            gunicorn_error_logger.critical("**********Request transactions failed. to_addr_{}******".format(transactions_conf["receiver"]))
    if order: order.save()
    return make_data()
    