# -*- coding: utf-8 -*-
__author__ = 'xu'

asset_type = {
    "eth": 1,
    "neo": 2
}
tx_type = {
    "in_tx": 1,
    "out_tx": 2
}
swap_type = {
    "neo_to_eth": 1,
    "eth_to_neo": 2
}
order_type = {
    "unpay": 0,
    "paid": 1,
    "sent": 2,
    "completed": 3
}
send_tx_type = {
    "pending": 1,
    "verified": 2
}
send_tx_remark = {
    "order_matching": u"tx与订单匹配",
    "order_mismatching": u"tx与订单不匹配"
}