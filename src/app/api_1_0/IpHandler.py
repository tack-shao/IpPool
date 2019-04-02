# -*- coding: utf-8 -*-
# @时间      :2019/3/25 下午11:03
# @作者      :tack
# @网站      :
# @文件      :IpHandler.py
# @说明      :

import json

from peewee import fn
from flask import request
from flask_json import as_json

from . import api
from .conf import *
from ..models import Ip
from ..util.schema import serializer_schema
from ..util.log import *

from ..util.PRPCrypt import PRPCrypt


# 加密类
prp = PRPCrypt(data_crypt_key)


@api.route('/ip', methods=['post'])
def get():
    """获取ip"""
    num = request.args.get('num', 1)
    raw_resp = {'status': -1, 'message': 'FAIL', 'result': ''}

    if num == '':
        num = '1'

    try:
        records = Ip.select().order_by(fn.Rand()).limit(int(num))
        raw_resp["status"] = 0
        raw_resp["message"] = "SUCCESS"
        raw_resp["result"] = [str(record) for record in records]
    except Exception as e:
        raw_resp["status"] = -1
        raw_resp["message"] = "FAIL"
        raw_resp["result"] = str(e)

    return json.dumps(raw_resp)


@api.route('/del', methods=['post'])
def delete():
    """删除一个ip"""
    ip = request.args.get('ip', '')
    raw_resp = {'status': -1, 'message': 'FAIL', 'result': ''}
    if ip == '':
        print('参数为空')
        raw_resp["result"] = '参数为空'
    else:
        ips = ip.split(',')
        try:
            nrows = Ip.delete().where(Ip.ip << ips).execute()
            raw_resp["status"] = 0
            raw_resp["message"] = "SUCCESS"
            raw_resp["result"] = "deleted %d records." % nrows
        except Exception as e:
            raw_resp["status"] = -1
            raw_resp["message"] = "FAIL"
            raw_resp["result"] = str(e)

    return json.dumps(raw_resp)

