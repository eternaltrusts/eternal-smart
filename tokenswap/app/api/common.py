# -*- coding: utf-8 -*-

from flask_restful import Resource

class CommonResource(Resource):
    def __init__(self, **kwargs):
        # smart_engine is a black box dependency
        self.models = kwargs['models']
        self.utils = kwargs['utils']
