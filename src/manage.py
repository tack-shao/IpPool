# -*- coding: utf-8 -*-
# @时间      :2019/3/23 下午6:58
# @作者      :tack
# @网站      :
# @文件      :manage.py
# @说明      :

import os
COV = None
if os.environ.get("IPPOOL_API_COVERAGE"):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app
from flask_script import Manager

app = create_app(os.getenv("IPPOOL_API_CONFIG") or 'default')
manager = Manager(app)


@manager.command
def test(coverage=False):
    """运行测试覆盖"""
    if coverage and not os.environ.get("IPPOOL_API_COVERAGE"):
        import sys
        os.environ["IPPOOL_API_COVERAGE"] = 1
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Converage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """在代码探测器下启动应用"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


def deploy():
    """运行发布任务"""
    from flask_migrate import upgrade
    # 数据库迁移
    upgrade()


if __name__ == "__main__":
    manager.run()
