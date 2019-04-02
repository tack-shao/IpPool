# -*- coding: utf-8 -*-
# @时间      :2019/3/23 下午6:56
# @作者      :tack
# @网站      :
# @文件      :__init__.py.py
# @说明      :

from flask import Flask
from flask_peewee.db import Database


from config import config

db = None


def create_app(config_name):
    global db
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    try:
        database = Database(app)
        db = database.database
    except Exception as e:
        print(e)
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        pass

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

    # 启动爬虫线程

    from app.spider import ip_pool_handle
    ip_pool_handle.dowork()
    print('测试测试测试')
    return app
