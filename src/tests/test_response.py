# -*- coding: utf-8 -*-
# @时间      :2019/3/27 上午1:05
# @作者      :tack
# @网站      :
# @文件      :test_response.py
# @说明      :

import unittest

from app.util.PRPCrypt import *
from app.api_1_0.conf import *

# 加密类
prp = PRPCrypt(data_crypt_key)


class TestResponse(unittest.TestCase):
    @unittest.skip
    def test_resp(self):
        s = "1237689798dasdkjashjdhkajsdh"
        enc_s = prp.encrypt(s)
        print(enc_s, type(enc_s))
        dnc_resp = prp.decrypt(enc_s)
        print(dnc_resp)
