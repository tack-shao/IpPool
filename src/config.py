# -*- coding: utf-8 -*-
# @时间      :2019/3/23 下午6:59
# @作者      :tack
# @网站      :
# @文件      :config.py
# @说明      :

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    IPPOOL_API_MAIL_SUBJECT_PREFIX = '[IpPoolApi]'
    IPPOOL_API_MAIL_SENDER = 'IpPool Admin '
    IPPOOL_API_ADMIN = os.environ.get('IPPOOL_API_ADMIN')
    IPPOOL_API_SLOW_DB_QUERY_TIME = 0.5
    JSON_ADD_STATUS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    # 开发环境配置
    DEBUG = True
    DATABASE = {
        "name": "ip_pool",
        "engine": "peewee.MySQLDatabase",
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "passwd": os.environ.get("SERV_MYSQL_PASSWD")
    }


class TestConfig(Config):
    # 测试环境配置
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE = {
        "name": "ip_pool",
        "engine": "peewee.MySQLDatabase",
        "host": os.environ.get("SERV_SSH_HOST"),
        "port": os.environ.get("3306"),
        "user": os.environ.get("SERV_MYSQL_USER"),
        "passwd": os.environ.get("SERV_MYSQL_PASSWD")
    }


class ProdConfig(Config):
    # 生产环境配置
    DEBUG = False
    DATABASE = {
        "name": "ip_pool",
        "engine": "peewee.MySQLDatabase",
        "host": os.environ.get("SERV_SSH_HOST"),
        "port": os.environ.get("3306"),
        "user": os.environ.get("SERV_MYSQL_USER"),
        "passwd": os.environ.get("SERV_MYSQL_PASSWD")
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, "MAIL_USERNAME", None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS", None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.IPPOOL_API_MAIL_SENDER,
            toaddrs=[cls.IPPOOL_API_ADMIN],
            subject=cls.IPPOOL_API_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class UnixConfig(ProdConfig):
    @classmethod
    def init_app(cls, app):
        ProdConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    "dev": DevConfig,
    "tests": TestConfig,
    "prod": ProdConfig,
    "unix": UnixConfig,
    "default": UnixConfig
}
