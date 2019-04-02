# -*- coding: utf-8 -*-
# @时间      :2019/3/22 下午11:52
# @作者      :tack
# @网站      :
# @文件      :__init__.py.py
# @说明      :

from flask import Blueprint

api = Blueprint('api', __name__)

from . import IpHandler