# -*- coding: utf-8 -*-
__author__ = 'xu'

import os
from functools import wraps

from flask import Flask, Blueprint, jsonify
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_login import  LoginManager
from flask_restful import Api

app = Flask(__name__)
APP_ENV = 'dev'
if not os.environ.has_key('APP_ENV') or os.environ['APP_ENV'].lower() == 'dev':
    print 'Running on Dev Env:'
    app.config.from_object('config')
elif os.environ['APP_ENV'].lower() in ('prod', 'test'):
    print 'Running on %s Env:' %os.environ['APP_ENV'].upper()
    app.config.from_object('config')
    app.config.from_object('config_' + os.environ['APP_ENV'].lower())
    APP_ENV = os.environ['APP_ENV'].lower()
else:
    print 'Wrong Env!'
    exit(1)
app.config["APP_ENV"] = APP_ENV
if not os.environ.has_key("VERIFY_HEADER_NAME") or not os.environ.has_key("VERIFY_PASSWORD") or not os.environ.has_key("VERIFY_HASHED"):
    print 'Wrong Env!'
    exit(1)
app.config["API_VERIFY"] = {
    "verify_header": os.environ['VERIFY_HEADER_NAME'],
    "password": os.environ["VERIFY_PASSWORD"],
    "hashed": os.environ["VERIFY_HASHED"].replace("*", "$")
}
# print app.config["API_VERIFY"]
#db
db = Database(app)
auth = Auth(app, db)
toolbar = DebugToolbarExtension(app)


mail = Mail(app)



import models
import utils
utils.create_tables()
import views

# from api import ApiReset, ApiRegister, ApiLogin

# api_bp = Blueprint('api', __name__, url_prefix="/api")
# api = Api(api_bp, default_mediatype='application/json')

# resource_class_kwargs = {"models": models, "utils": utils}

# api.add_resource(
#     ApiLogin,
#     '/v1.0/login',
#     resource_class_kwargs=resource_class_kwargs
# )
# api.add_resource(
#     ApiRegister,
#     '/v1.0/register',
#     resource_class_kwargs=resource_class_kwargs
# )
# api.add_resource(
#     ApiReset,
#     '/v1.0/reset',
#     resource_class_kwargs=resource_class_kwargs
# )
# app.register_blueprint(api_bp)