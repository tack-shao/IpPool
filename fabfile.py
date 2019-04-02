# -*- coding: utf-8 -*-
# @时间      :2019/4/1 下午5:42
# @作者      :tack
# @网站      :
# @文件      :fabfile.py
# @说明      :


import os
from datetime import datetime

# 导入 Fabric API
from fabric.api import *

# 远程服务器用户
env.user = os.environ.get("SERV_SSH_LOGIN_USER")
# 远程服务器超级管理员用户
env.sudo_user = os.environ.get("SERV_SSH_LOGIN_SUDO_USER")
# 远程服务器host
env.hosts = os.environ.get("SERV_SSH_HOST")
env.password = os.environ.get("SERV_SSH_PASSWORD")

# 远程服务器 MYSQL 用户和密码:
db_user = os.environ.get("SERV_MYSQL_PASSWD")
db_pwd = os.environ.get("SERV_MYSQL_PASSWD")
db_port = os.environ.get("SERV_MYSQL_PORT")

# 打包的名字
_TAR_FILE = "dist-my-ip-pool.tar.gz"


def build():
    """
    打包
    :return:
    """
    includes = ['app', 'requirements', 'conf', '*.py']
    excludes = ['tests', '.*', '*.pyc', '*.pyo']
    local('rm -rf dist/%s' % _TAR_FILE)
    with lcd(os.path.join(os.path.abspath('.'), 'src')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(["--exclude='%s'" % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))


# 远程服务器的相关操作路径
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/root/www/'

_NGINX_CONF = "nginx_ippool.conf"
_SUPERVISOR_CONF = "supervisor_ippool.conf"


def deploy():
    """
    部署
    :return:
    """
    newdir = 'ippool-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    # 删除已有的 tar 文件
    run('rm -rf %s' % _REMOTE_TMP_TAR)
    # 删除已有的 tar 文件
    run('rm -rf %s/ippool*' %_REMOTE_BASE_DIR)
    # 上传新的 tar 文件
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    # 解压到新目录
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)

    # 创建新连接
    with cd(_REMOTE_BASE_DIR):
        sudo("rm -rf ippool")
        sudo("ln -s %s ippool" % newdir)
        sudo("chown root:root ippool")
        sudo("chown -R root:root %s" % newdir)

    # 安装supervisor
    sudo("yum install supervisor -y")
    sudo("cp %s/conf/%s %s/%s" % (os.path.join(_REMOTE_BASE_DIR, newdir), _SUPERVISOR_CONF, "/etc/supervisord.d", _SUPERVISOR_CONF))
    # 安装nginx
    sudo("yum install nginx -y")
    sudo("cp %s/conf/%s %s/%s" % (os.path.join(_REMOTE_BASE_DIR, newdir), _NGINX_CONF, "/etc/nginx/conf.d", _NGINX_CONF))

    # 安装python环境
    # sudo("mkvirtualenv -p python3 ippool")
    # 切换到ippool环境
    with prefix("workon ippool"):

        # 安装python包
        with cd("%s/%s/%s" % (_REMOTE_BASE_DIR, newdir, 'requirements')):
            sudo("pip install -r requirements.txt")

        # 重启 Python 服务和 nginx 服务器:
        with settings(warn_only=True):
            sudo('supervisorctl stop ippool')
            sudo('supervisorctl start ippool')
            sudo('nginx -s reload')


def test():
    """
    测试远程安装工具：python 环境 supervisor、gunicorn、gevent
    :return:
    """
    # sudo('yum install supervisor -y')
    sudo("mkvirtualenv -p python3 ippool")
    with prefix("workon ippool"):
        sudo("pip install gevent")
