# -*- coding: utf-8 -*-
# @时间      :2019/3/23 上午12:31
# @作者      :tack
# @网站      :
# @文件      :test_ippool.py
# @说明      :

import unittest
from app.spider.IpPool import IpPool


class test_ippool(unittest.TestCase):
    def test_do(self):
        ippool = IpPool()
        ippool.dowork()
        while True:
            pass

