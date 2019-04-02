# -*- coding: utf-8 -*-
# @时间      :2019/3/26 下午4:51
# @作者      :tack
# @网站      :
# @文件      :test_schema.py
# @说明      :

import unittest
import json

from app.models import Ip
from app.util.schema import *


class TestSchema(unittest.TestCase):
    @unittest.skip
    def test_do(self):

        ip = Ip()
        ip.ip = "127.0.0.1"
        ip.port = '3306'
        ip.address = '广东深圳'
        re, er = serializer_schema(Ip).dump(ip)
        print(re)
