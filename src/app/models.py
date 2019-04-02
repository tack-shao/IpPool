# -*- coding: utf-8 -*-
# @Time      :2019/3/22 下午1:29
# @Author    :tack
# @Site      :
# @File      :models.py
# @Software  :PyCharm

import datetime, json
from flask_peewee.db import Model, AutoField, CharField, DateTimeField

from . import db


class Ip(Model):
    id = AutoField(primary_key=True)
    ip = CharField(max_length=16, null=False, default="", unique=True)
    port = CharField(max_length=5, null=False, default="")
    address = CharField(max_length=30, default="")
    ip_type = CharField(max_length=8)
    create_time = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        r = {}
        for k in self.__data__.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)

    class Meta:
        database = db
        table_name = "ip"
