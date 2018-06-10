# -*- coding: utf-8 -*-
__author__ = 'xu'

from werkzeug.security import generate_password_hash,check_password_hash
from flask_peewee.admin import Admin, ModelAdmin
from flask_security import UserMixin, RoleMixin, PeeweeUserDatastore, Security
from peewee import TextField, BooleanField, DateTimeField, DateField,\
    ForeignKeyField, CharField, FloatField,IntegerField, DecimalField, IntegrityError
from playhouse.signals import Signal
from hashlib import md5
import random,time
from datetime import datetime
from . import  app,auth, db
import types

before_save = Signal()
after_save = Signal()

class SignalModel(db.Model):
    def save(self, *args, **kwargs):
        created = not bool(self.get_id())
        before_save.send(self, created=created)
        super(SignalModel, self).save(*args, **kwargs)
        after_save.send(self, created=created)

class Order(db.Model):
    tx_no = CharField(verbose_name=u"交易编号", null=True, index=True)
    sender = CharField(verbose_name=u"付款方")
    receiver = CharField(verbose_name=u"收款方")
    send_value = CharField(verbose_name=u"发送金额")
    receiver_value = CharField(verbose_name=u"接收金额")
    swap_type = CharField(verbose_name=u"转换类型")
    tax_cost = CharField(verbose_name=u"手续费")
    created_time = DateTimeField(verbose_name=u"创建时间", index=True)
    pay_complete_time = DateTimeField(verbose_name=u"支付完成时间", null=True)
    rev_complete_time = DateTimeField(verbose_name=u"收款完成时间", null=True)
    in_tx = CharField(verbose_name=u"转入tx_id", null=True)
    out_tx = CharField(verbose_name=u"转出tx_id", null=True)
    status = IntegerField(
        verbose_name=u"订单状态",
        choices=(
            (types.order_type["unpay"], 'unpay'),
            (types.order_type["paid"], 'paid'),
            (types.order_type["sent"], 'sent'),
            (types.order_type["completed"], 'completed')
        ),
        default=types.order_type["unpay"], 
        index=True
    )

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if not self.tx_no:
            self.tx_no = self.created_time.strftime("%m%d%f") + str(random.randint(10000, 99999))
            if Order.get_or_none(Order.tx_no == self.tx_no):
                self.tx_no = self.tx_no + str(self.id)
            self.tx_no = "order_no" + self.tx_no
            self.save()
    @classmethod
    def get_order_by_tx_no(cls, tx_no):
        return cls.get_or_none(cls.tx_no == tx_no)
    
    @classmethod
    def check_exist_unpay_order(cls, sender):
        orders = cls.select().where(
            cls.sender == sender,
            cls.status < 3
        )
        # print(orders.count())
        return orders.count()

    @classmethod
    def create_order(cls, **kwargs):
        order = cls.create(
            sender = kwargs.get("sender"),
            swap_type = kwargs.get("swap_type"),
            receiver = kwargs.get("receiver"),
            send_value = kwargs.get("send_value"),
            receiver_value = kwargs.get("receiver_value"),
            tax_cost = kwargs.get("tax_cost"),
            created_time = kwargs.get("created_time"),
        )
        return order

    @classmethod
    def get_order_by_filter(cls, *multi_filter):
        order = cls.select().where(*multi_filter).first()
        return order

class SendTransactions(db.Model):
    """
    发出去的交易,有两种状态: 0:待确认的交易;1:已确认的交易
    """
    tx_id = CharField(verbose_name=u"交易tx_id")
    sender = CharField(verbose_name=u"付款方")
    receiver = CharField(verbose_name=u"收款方")
    value = CharField(verbose_name=u"发送金额")
    created_time = DateTimeField(verbose_name=u"创建时间", default=datetime.now())
    complete_time = DateTimeField(verbose_name=u"完成时间", null=True)
    remark = CharField(
        verbose_name=u"发送交易备注",
        help_text=u"""remark 有两个类型,分别是:\n
        order_matching": "订单匹配, token转换成功", \n
        order_mismatching": "订单存在, 但信息不匹配, token退回",\n
        """
    )
    status = IntegerField(
        verbose_name=u"交易状态",
        choices=((types.send_tx_type["pending"], "pending"),(types.send_tx_type["verified"], 'verified')), 
        default=types.send_tx_type["pending"],
        index=True
    )
    asset_type = IntegerField(
        verbose_name=u"资产类型", 
        choices=((types.asset_type["neo"], "neo"),(types.asset_type["eth"], "eth"))
    )


    # order = ForeignKeyField(Order, )
class MonitorTransactions(db.Model):
    """
    已经上链的交易,表示已经成功的交易
    """
    tx_id = CharField(verbose_name=u"交易tx_id", unique=True)
    sender = CharField(verbose_name=u"付款方")
    receiver = CharField(verbose_name=u"收款方")
    value = CharField(verbose_name=u"交易金额")
    created_time = DateTimeField(verbose_name=u"创建时间", null=True)
    complete_time = DateTimeField(verbose_name=u"完成时间", null=True)
    asset_type = IntegerField(
        verbose_name=u"资产类型", 
        choices=((types.asset_type["neo"], "neo"),(types.asset_type["eth"], "eth"))
    )
    tx_type = IntegerField(
        verbose_name=u"交易类型", 
        choices=((types.tx_type["in_tx"], "in_tx"),(types.tx_type["out_tx"], 'out_tx'))
    )


    # order = ForeignKeyField(Order, index=True)

class OrderAdmin(ModelAdmin):
    columns = ("receiver", "receiver_value", "send_value", "swap_type", "status", "tx_no")

class SendTransactionsAdmin(ModelAdmin):
    columns = ("receiver", "value", "asset_type", "status", "remark")

class MonitorTransactionsAdmin(ModelAdmin):
    columns = ("tx_id", "value", "asset_type", "tx_type")

# Setup Flask-Security
# user_datastore = PeeweeUserDatastore(db, Users, Role, UserRoles)
# security = Security(app, user_datastore)


# create admin object
admin = Admin(app, auth, prefix=app.config['ADMIN_URL'], branding=app.config['BRANDING'], )
# admin.register(Users, ModelAdmin)
# admin.register(Role, ModelAdmin)
# admin.register(UserRoles, ModelAdmin)
admin.register(Order, OrderAdmin)
admin.register(SendTransactions, SendTransactionsAdmin)
admin.register(MonitorTransactions, MonitorTransactionsAdmin)
auth.register_admin(admin)

admin.setup()
